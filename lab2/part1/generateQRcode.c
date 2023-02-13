#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#include "lib/encoding.h"

int
main(int argc, char * argv[])
{
	if ( argc != 4 ) {
		printf("Usage: %s [issuer] [accountName] [secretHex]\n", argv[0]);
		return(-1);
	}

	char *	issuer = argv[1];
	char *	accountName = argv[2];
	char *	secret_hex = argv[3];

	// TODO: delete printf
	// printf("%s, %s, %s\n", issuer, accountName, secret_hex);

	assert (strlen(secret_hex) <= 20);

	// URL-encode issuer string
	const char * issuer_encoded = urlEncode(issuer);
	// URL-encode account name string
	const char * accountName_encoded = urlEncode(accountName);

	uint8_t secret_int[10];
	for (size_t i = 0; i < 10; ++i) {
        sscanf(secret_hex + i * 2, "%2hhx", secret_int + i);
    }
    char secret_base32[17];
    base32_encode(secret_int, 10, (uint8_t *) secret_base32, 17);

	printf("\nIssuer: %s\nAccount Name: %s\nSecret (Hex): %s\n\n",
		issuer_encoded, accountName_encoded, secret_hex);

	const char URI[15 + strlen(accountName) + 8 + strlen(issuer) + 8 + 10];
	sprintf((char *) URI, "otpauth://totp/%s?issuer=%s&secret=%s&period=30", accountName_encoded, issuer_encoded, secret_base32);

	// Create an otpauth:// URI and display a QR code that's compatible
	// with Google Authenticator

	displayQRcode(URI);

	return (0);
}
