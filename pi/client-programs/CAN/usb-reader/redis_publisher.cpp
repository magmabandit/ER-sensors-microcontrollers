#include "redis_publisher.hpp"

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
void publish_can_message(redisContext* redis, const struct can_frame* frame) {
    if (!redis) return;

        // Create a JSON object for the CAN frame
        cJSON *json = cJSON_CreateObject();
        cJSON_AddNumberToObject(json, "can_id", frame->can_id);
        cJSON_AddNumberToObject(json, "can_dlc", frame->can_dlc);

        cJSON *data_array = cJSON_CreateArray();
        for (int i = 0; i < frame->can_dlc; i++) {
            cJSON_AddItemToArray(data_array, cJSON_CreateNumber(frame->data[i]));
        }
        cJSON_AddItemToObject(json, "data", data_array);

        char *message = cJSON_PrintUnformatted(json);

        redisReply* reply = (redisReply*)redisCommand(redis, "PUBLISH %s %s", REDIS_CHANNEL, message);
        if (reply) freeReplyObject(reply);

        free(message);
        cJSON_Delete(json);
    }

// DEBUG: reading from file instead of usb

// Function to read CAN messages from a file
void read_can_from_file(const char *filename, redisContext *redis) {
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

// Comment out main so this will compile with canusb.c
//int main() {
//    redisContext *redis = connect_redis();
//    if (!redis) return EXIT_FAILURE;
//
//    printf("Reading CAN messages from file: %s\n", TEST_FILE);
//    read_can_from_file(TEST_FILE, redis);
//
//    redisFree(redis);
//    return EXIT_SUCCESS;
//}
