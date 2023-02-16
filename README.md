#Ching Hui, 1005219504, sam.hui@mail.utoronto.ca
#Spencer Ball, , spencer.ball@mail.utoronto.ca

Part 1

generateQRcode.c:
URL-encode the issuer and account name, then read the hexadecimal secret into binary (10 of uint8_t). 
Encode the secret into base 32, format the URI, and display the QR code.

validateQRcode.c:
Compute HMAC following the definition, using (Unix-time / 30) as the message, 
and follow the code provided in RFC6238 to truncate the computed HMAC to 6 characters.
