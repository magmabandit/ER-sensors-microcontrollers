#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

// These 2 packages need to be installed on the RPIs
#include <hiredis/hiredis.h>
#include <cjson/cJSON.h>

#define REDIS_HOST "127.0.0.1"
#define REDIS_PORT 6379
#define REDIS_CHANNEL "canusb_data"
#define RECONNECT_DELAY 5
#define TEST_FILE "data.txt"

struct can_frame {
    int can_id;
    int can_dlc;
    unsigned char data[8];
};

// Function to establish Redis connection
redisContext* connect_redis() {
    redisContext *c = redisConnect(REDIS_HOST, REDIS_PORT);
    if (c == NULL || c->err) {
        if (c) {
            printf("Redis connection error: %s\n", c->errstr);
            redisFree(c);
        } else {
            printf("Redis connection allocation error\n");
        }
        return NULL;
    }
    printf("Connected to Redis successfully.\n");
    return c;
}

// Function to publish CAN message to Redis
void publish_can_message(redisContext **c, struct can_frame *frame) {
    if (!(*c) || !frame) return;

    redisReply *ping_reply = redisCommand(*c, "PING");
    if (!ping_reply) {
        printf("Redis connection lost. Attempting to reconnect...\n");
        redisFree(*c);
        *c = NULL;
        while (!(*c)) {
            *c = connect_redis();
            if (*c) {
                printf("Reconnected to Redis.\n");
                break;
            }
            printf("Reconnection failed, retrying in %d seconds...\n", RECONNECT_DELAY);
            sleep(RECONNECT_DELAY);
        }
        return;
    }
    freeReplyObject(ping_reply);

    cJSON *json = cJSON_CreateObject();
    cJSON_AddNumberToObject(json, "id", frame->can_id);
    cJSON_AddNumberToObject(json, "dlc", frame->can_dlc);

    cJSON *data_array = cJSON_CreateArray();
    for (int i = 0; i < frame->can_dlc; i++) {
        cJSON_AddItemToArray(data_array, cJSON_CreateNumber(frame->data[i]));
    }
    cJSON_AddItemToObject(json, "data", data_array);

    char *json_str = cJSON_PrintUnformatted(json);

    redisReply *reply = redisCommand(*c, "PUBLISH %s %s", REDIS_CHANNEL, json_str);
    if (reply) {
        freeReplyObject(reply);
    } else {
        printf("Redis publish error: %s\n", (*c)->errstr);
    }

    free(json_str);
    cJSON_Delete(json);
}

// Function to read CAN messages from a file
void read_can_from_file(const char *filename, redisContext **redis) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        perror("Error opening test file");
        return;
    }

    char line[256];
    while (fgets(line, sizeof(line), file)) {
        // Parse the line
        double timestamp;
        unsigned int frame_id;
        unsigned char data[8];
        int data_length = 0;

        // Extract timestamp, frame ID, and data
        if (sscanf(line, "%lf Frame ID: %x, Data: %hhx %hhx %hhx %hhx %hhx %hhx %hhx %hhx",
                   &timestamp, &frame_id,
                   &data[0], &data[1], &data[2], &data[3],
                   &data[4], &data[5], &data[6], &data[7]) >= 9) {
            // Determine the actual data length
            data_length = 8;  // Assuming all CAN frames have 8 bytes of data

            // Create a CAN frame
            struct can_frame frame;
            frame.can_id = frame_id;
            frame.can_dlc = data_length;
            memcpy(frame.data, data, data_length);

            printf("Publish CAN message...");
            publish_can_message(redis, &frame);

            // Simulate delay between CAN messages
            sleep(1);
        } else {
            printf("Error parsing line: %s\n", line);
        }
    }

    fclose(file);
}

int main() {
    redisContext *redis = connect_redis();
    if (!redis) return EXIT_FAILURE;

    printf("Reading CAN messages from file: %s\n", TEST_FILE);
    read_can_from_file(TEST_FILE, &redis);

    redisFree(redis);
    return EXIT_SUCCESS;
}

