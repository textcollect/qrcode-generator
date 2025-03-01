# QR Code Generator (Prototype)

This is just a proof-of-concept, made for learning purposes. It is not fit for production usage but it does *work*.  
Note: 1=black, 0=white

Steps to create a qr code:
0. Determine the size of qr code. Different versions hav different sizes.
1. Create the 3 boxes
2. Create the 4th box at the bottom-right
3. Convert the text into binary, based on their ascii representation
4. Fill up from bottom-right, to top, 2 columns at the same time, going in a zig-zag, right-left direction
5. If reached the top, move to left and do the same in downward direction, going in a snake direction.
6. If touched one of the squares, ignore and continue.