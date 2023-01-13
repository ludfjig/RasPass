#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <stdint.h>
#include <sstream>

// Pico Libraries
#include "pico/stdlib.h"

// storage in flash for data
const uint8_t *flash_data = (const uint8_t*) (XIP_BASE + (1536*1024));


int main() {
  // stdio/board init
  stdio_init_all();

  printf("Hello world");

  while (1);
}
