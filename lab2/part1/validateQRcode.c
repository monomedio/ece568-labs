#include <stdio.h>
#include <string.h>
#include <assert.h>

#include "lib/sha1.h"
#include <time.h>


static int
validateTOTP(char * secret_hex, char * TOTP_string)
{
	// Convert secret_hex string to binary
	uint8_t secret_int[64];
	memset(secret_int, 0, 64);
	for (size_t i = 0; i < 10; ++i) {
        sscanf(secret_hex + i * 2, "%2hhx", secret_int + i);
    }

    // Initialize inner and outer paddings
	uint8_t i_padded[64];
	uint8_t o_padded[64];
	memset(i_padded, 0x36, 64);
	memset(o_padded, 0x5c, 64);

	// XORing
	for (int i = 0; i < 10; i++) {
		i_padded[i] ^= secret_int[i];
		o_padded[i] ^= secret_int[i];
	}

	// Converting a 64-bit int to an array of 8-bit ints
	uint64_t counter = time(NULL) / 30;
	uint8_t message[8];
	for (int i = 7; i >= 0; i--) {
        message[i] = counter & 0xff;
        counter >>= 8;
    }

    // Hashing
    SHA1_INFO ctx;
    uint8_t inner[SHA1_DIGEST_LENGTH];
    uint8_t outer[SHA1_DIGEST_LENGTH];
    sha1_init(&ctx);
    sha1_update(&ctx, i_padded, 64);
    sha1_update(&ctx, (uint8_t *)message, 8);
    sha1_final(&ctx, inner);
    sha1_init(&ctx);
    sha1_update(&ctx, o_padded, 64);
    sha1_update(&ctx, inner, 20);
    sha1_final(&ctx, outer);

    // Putting selected bytes into result int
    int offset = outer[SHA1_DIGEST_LENGTH - 1] & 0xf;
    int binary = ((outer[offset] & 0x7f) << 24) |
        ((outer[offset + 1] & 0xff) << 16) |
        ((outer[offset + 2] & 0xff) << 8) |
        (outer[offset + 3] & 0xff);
    int otp = binary % 1000000;

    char res[7];
    snprintf(res, 7, "%06d", otp);

	return strncmp(res, TOTP_string, 6) == 0;
}


int
main(int argc, char * argv[])
{
	if ( argc != 3 ) {
		printf("Usage: %s [secretHex] [TOTP]\n", argv[0]);
		return(-1);
	}

	char *	secret_hex = argv[1];
	char *	TOTP_value = argv[2];

	assert (strlen(secret_hex) <= 20);
	assert (strlen(TOTP_value) == 6);

	printf("\nSecret (Hex): %s\nTOTP Value: %s (%s)\n\n",
		secret_hex,
		TOTP_value,
		validateTOTP(secret_hex, TOTP_value) ? "valid" : "invalid");

	return(0);
}
