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

