#ifndef REDIS_PUBLISHER_HPP
#define REDIS_PUBLISHER_HPP

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
#define TEST_FILE "data3.txt" // DEBUG

struct can_frame {
    int can_id;
    int can_dlc;
    unsigned char data[8];
};

// Function to establish Redis connection
redisContext* connect_redis();

// Function to publish CAN message to Redis
void publish_can_message(redisContext* redis, const can_frame* frame);

#endif // REDIS_PUBLISHER_HPP
