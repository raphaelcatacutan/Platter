SYNTAX_TSCRIPTS = [
  {
    "number": 1,
    "expected_output": """No Syntax Error""",
    "code": """flag of x = (x + 1) * ("HELLO") > 1; 
start() {}"""
  },
  {
    "number": 2,
    "expected_output": """No Syntax Error""",
    "code": """flag of a = (x + "hello") > "Hello";
start() {}"""
  },
  {
    "number": 3,
    "expected_output": """No Syntax Error""",
    "code": """flag of a = (x + "hello") > 1; 
start() {}"""
  },
  {
    "number": 4,
    "expected_output": """No Syntax Error""",
    "code": """flag of a = (x + 1) > "Hello";
start() {}"""
  },
  {
    "number": 5,
    "expected_output": """No Syntax Error""",
    "code": """flag of x = 1 * 1 < 3 and up;
start() {}"""
  },
  {
    "number": 6,
    "expected_output": """Syntax Error: Unexpected 'piece_lit' at line 1, col 19. Expected 'id', 'sqrt', 'rand', 'tosip', 'sip_lit', '('.""",
    "code": """flag of x = 1.2 < 3;
start() {}"""
  },
  {
    "number": 7,
    "expected_output": """Syntax Error: Unexpected ';' at line 1, col 18. Expected '*', '/', '%', '+', '-', '==', '!=', '>=', '<=', '<', '>'.""",
    "code": """flag of x = 1 * 1;
start() {}"""
  },
  {
    "number": 8,
    "expected_output": """No Syntax Error""",
    "code": """flag of x = 1 * 1 < 3 and up; # allowed
start() {}"""
  },
  {
    "number": 9,
    "expected_output": """No Syntax Error""",
    "code": """flag of x = topiece(y) > x + 1;
start() {}"""
  },
  {
    "number": 10,
    "expected_output": """Syntax Error: Unexpected ',' at line 2, col 25. Expected '*', '/', '%', '+', '-', ')'.""",
    "code": """start() {
    pass(a = 1; a += (1 , +2) ; a < 10) { }
}"""
  },
  {
    "number": 11,
    "expected_output": """Syntax Error: Unexpected 'piece_lit' at line 2, col 23. Expected 'bill', 'take', 'copy', 'cut', 'tochars', 'chars_lit', 'id', '('.""",
    "code": """start() {
    x = x + "hello" + 1;
}"""
  },
  {
    "number": 12,
    "expected_output": """Syntax Error: Unexpected 'chars_lit' at line 2, col 20. Expected 'topiece', 'size', 'search', 'fact', 'pow', 'piece_lit', 'sqrt', 'rand', 'tosip', 'sip_lit', 'id', '('.""",
    "code": """start() {
    repeat((x+5) * "abc" == 5){ }
}"""
  },
  {
    "number": 13,
    "expected_output": """Syntax Error: Unexpected 'chars_lit' at line 1, col 21. Expected 'topiece', 'size', 'search', 'fact', 'pow', 'piece_lit', 'id', '('.""",
    "code": """flag of x = X + 1 > "asd";
start() {}"""
  },
  {
    "number": 14,
    "expected_output": """No Syntax Error""",
    "code": """table of A = [ piece of a; piece of b; ];
prepare piece of sum(A of x){
    serve x:a + x:b;
}
start(){
    A of t = [a = 4; b = 6;];
    bill(tochars(sum(t)));
}"""
  },
  {
    "number": 15,
    "expected_output": """No Syntax Error""",
    "code": """table of Dim = [ piece of w; ];
table of Box = [ Dim of d; ];
start(){
    Box of b = [d = [w = 15;];];
    bill(tochars(b:d:w + 5));
}"""
  },
  {
    "number": 16,
    "expected_output": """Syntax Error: Unexpected '-' at line 6, col 22. Expected 'topiece', 'size', 'search', 'fact', 'pow', 'piece_lit', 'sqrt', 'rand', 'tosip', 'sip_lit', 'matches', 'flag_lit', 'bill', 'take', 'copy', 'cut', 'tochars', 'chars_lit', 'id', '(', 'not'.""",
    "code": """start(){
    piece of x = 7;
    check(x > 0){
        bill(tochars(x * x));
    } instead {
        bill(tochars(-x));
    }
}"""
  },
  {
    "number": 17,
    "expected_output": """No Syntax Error""",
    "code": """table of Item = [ piece of id; ];
start(){
    Item[] of list = [[id=10;], [id=20;]];
    bill(tochars(list[1]:id));
}"""
  },
  {
    "number": 18,
    "expected_output": """No Syntax Error""",
    "code": """start(){
    piece[] of a = [1, 2, 3];
    piece of i = 2;
    repeat(i >= 0){
        bill(tochars(a[i]) + " ");
        i -= 1;
    }
}"""
  },
  {
    "number": 19,
    "expected_output": """No Syntax Error""",
    "code": """table of T = [ piece of v; ];
start(){
    T of a = [v = 5;], b = [v = 8;];
    bill(tochars(a:v < b:v));
}"""
  },
  {
    "number": 20,
    "expected_output": """No Syntax Error""",
    "code": """table of Node = [ piece of v; ];
start(){
    Node[] of nodes = [[v=1;], [v=2;], [v=3;]];
    bill(tochars(size(nodes)));
}"""
  },
  {
    "number": 21,
    "expected_output": """No Syntax Error""",
    "code": """start(){
    piece of a = 5, b = 3;
    bill(tochars((a*a + b*b) > 30));
}"""
  },
  {
    "number": 22,
    "expected_output": """No Syntax Error""",
    "code": """start(){
    piece of x = 4, y = 9;
    x = x + y;
    y = x - y;
    x = x - y;
    bill(tochars(x) + " " + tochars(y));
}"""
  },
  {
    "number": 23,
    "expected_output": """No Syntax Error""",
    "code": """start(){
    piece of n = 12345, c = 0;
    repeat(n != 0){
        c += 1;
        n /= 10;
    }
    bill(tochars(c));
}"""
  },
  {
    "number": 24,
    "expected_output": """No Syntax Error""",
    "code": """table of P = [
    piece of x;
    piece of y;
];
start(){
    P of p = [x = 3; y = 7;];
    bill(tochars(p:x + p:y));
}"""
  },
  {
    "number": 25,
    "expected_output": """No Syntax Error""",
    "code": """start(){
    piece of n = 123, r = 0;
    repeat(n != 0){
        r = r * 10 + n % 10;
        n /= 10;
    }
    bill(tochars(r));
}"""
  },
  {
    "number": 26,
    "expected_output": """No Syntax Error""",
    "code": """start(){
    piece of n = 11;
    check(n % 2 != 0){
        bill("odd");
    } instead {
        bill("even");
    }
}"""
  },
  {
    "number": 27,
    "expected_output": """No Syntax Error""",
    "code": """start(){
    piece of a = 3, b = 9, c = 6, m;
    check(a > b){
        check(a > c){ m = a; } instead { m = c; }
    } instead {
        check(b > c){ m = b; } instead { m = c; }
    }
    bill(tochars(m));
}"""
  },
  {
    "number": 28,
    "expected_output": """No Syntax Error""",
    "code": """table of S = [ piece of v; ];
start(){
    S[] of s = [
        [v = 1;], 
        [v = 2;], 
        [v = 3;]
    ];
    chars of printing = tochars(s[0]:v + s[1]:v + s[2]:v);
    bill(printing);
}"""
  },
  {
    "number": 29,
    "expected_output": """No Syntax Error""",
    "code": """start(){
    piece of i = 65;
    repeat(i <= 69){
        bill(tochars(i) + " ");
        i += 1;
    }
}"""
  },
  {
    "number": 30,
    "expected_output": """No Syntax Error""",
    "code": """start(){
    piece of n = 5, f = 1;
    repeat(n > 0){
        f *= n;
        n -= 1;
    }
    bill(tochars(f));
}"""
  },
  {
    "number": 31,
    "expected_output": """No Syntax Error""",
    "code": """start(){
    piece of n = 121, t = n, r = 0;
    repeat(t != 0){
        r = r * 10 + t % 10;
        t /= 10;
    }
    bill(tochars(r == n));
}"""
  },
  {
    "number": 32,
    "expected_output": """No Syntax Error""",
    "code": """start(){
    piece of x = 10;
    piece of p = x;
    bill(tochars(p + 5));
}"""
  },
  {
    "number": 33,
    "expected_output": """No Syntax Error""",
    "code": """start(){
    piece of n = 13, c = 0;
    repeat(n > 0){
        c += n % 2;
        n /= 2;
    }
    bill(tochars(c));
}"""
  },
  {
    "number": 34,
    "expected_output": """No Syntax Error""",
    "code": """table of A = [ piece of a; piece of b; ];
prepare piece of sum(A of x){
    serve x:a + x:b;
}
start(){
    A of t = [a = 4; b = 6;];
    bill(tochars(sum(t)));
}"""
  },
  {
    "number": 35,
    "expected_output": """No Syntax Error""",
    "code": """table of Dim = [ piece of w; ];
table of Box = [ Dim of d; ];
start(){
    Box of b = [d = [w = 15;];];
    bill(tochars(b:d:w + 5));
}"""
  },
  {
    "number": 36,
    "expected_output": """Syntax Error: Unexpected '-' at line 6, col 22. Expected 'topiece', 'size', 'search', 'fact', 'pow', 'piece_lit', 'sqrt', 'rand', 'tosip', 'sip_lit', 'matches', 'flag_lit', 'bill', 'take', 'copy', 'cut', 'tochars', 'chars_lit', 'id', '(', 'not'.""",
    "code": """start(){
    piece of x = 7;
    check(x > 0){
        bill(tochars(x * x));
    } instead {
        bill(tochars(-x));
    }
}"""
  },
  {
    "number": 37,
    "expected_output": """No Syntax Error""",
    "code": """table of Item = [ piece of id; ];
start(){
    Item[] of list = [[id=10;], [id=20;]];
    bill(tochars(list[1]:id));
}"""
  },
  {
    "number": 38,
    "expected_output": """No Syntax Error""",
    "code": """start(){
    piece[] of a = [1, 2, 3];
    piece of i = 2;
    repeat(i >= 0){
        bill(tochars(a[i]) + " ");
        i -= 1;
    }
}"""
  },
  {
    "number": 39,
    "expected_output": """No Syntax Error""",
    "code": """table of T = [ piece of v; ];
start(){
    T of a = [v = 5;], b = [v = 8;];
    bill(tochars(a:v < b:v));
}"""
  },
  {
    "number": 40,
    "expected_output": """No Syntax Error""",
    "code": """table of Node = [ piece of v; ];
start(){
    Node[] of nodes = [[v=1;], [v=2;], [v=3;]];
    bill(tochars(size(nodes)));
}"""
  },
  {
    "number": 41,
    "expected_output": """Syntax Error: Unexpected 'piece' at line 2, col 10. Expected 'id'.""",
    "code": """start(){
    pass(piece of i = 0; i += 3; i > 0){
        serve i;
    }
}"""
  },
  {
    "number": 42,
    "expected_output": """No Syntax Error""",
    "code": """piece[][] of grid = [1, 2];

start(){
    serve grid[0][0];
}"""
  },
  {
    "number": 43,
    "expected_output": """Syntax Error: Unexpected 'id' at line 5, col 14. Expected '('.""",
    "code": """start(){
    piece of x = 0;
    order{
        x += 1;
    } repeat x < 5;
    serve x;
}"""
  },
  {
    "number": 44,
    "expected_output": """Syntax Error: Unexpected 'piece_lit' at line 4, col 35. Expected 'id', 'sqrt', 'rand', 'tosip', 'sip_lit', '('.""",
    "code": """piece of x = 5;

start(){
    piece of x = topiece(rand() * 3) + 1;
    chars of s = copy("CompilerDesign", 0, 8);
    serve x * size(s);
}"""
  },
  {
    "number": 45,
    "expected_output": """Syntax Error: Unexpected token 'piece' after start platter, Expected EOF (line 4, col 1)""",
    "code": """start(){
    serve 0;
}
piece of x = 3;"""
  },
  {
    "number": 46,
    "expected_output": """No Syntax Error""",
    "code": """start(){
    repeat(not x < 5){
        serve x;
    }
}"""
  },
  {
    "number": 47,
    "expected_output": """Syntax Error: Unexpected 'serve' at line 2, col 1. Expected 'piece', 'chars', 'sip', 'flag', 'table', 'id', 'prepare', 'start'.""",
    "code": """piece of x = 3;
serve x;"""
  },
  {
    "number": 48,
    "expected_output": """Syntax Error: Unexpected 'serve' at line 4, col 7. Expected 'repeat'.""",
    "code": """start(){
    order{
        serve 1;
    } serve 2;
    repeat(x < 3);
}"""
  },
  {
    "number": 49,
    "expected_output": """No Syntax Error""",
    "code": """piece of x = 2;

start(){
    menu(x){
        choice 1: serve 10;
        choice 2: serve 20;
        usual: serve 0;
    }
}"""
  },
  {
    "number": 50,
    "expected_output": """No Syntax Error""",
    "code": """start(){
    serve (x + 1) * (y - 2);
}"""
  },
  {
    "number": 51,
    "expected_output": """Syntax Error: Unexpected 'id' at line 1, col 16. Expected '*', '/', '%', '+', '-', ',', ';'.""",
    "code": """piece of x = 5 y;
start(){
    serve x;
}"""
  },
  {
    "number": 52,
    "expected_output": """Syntax Error: Unexpected '(' at line 1, col 19. Expected 'id', 'append', 'sort', 'reverse', 'remove', '['.""",
    "code": """piece[] of nums = (1, 2, 3);

start(){
    serve nums[0];
}"""
  },
  {
    "number": 53,
    "expected_output": """Syntax Error: Unexpected 'stop' at line 3, col 5. Expected 'choice', 'usual', '}'.""",
    "code": """start(){
    menu(x + 1){
    stop;
    }
}"""
  },
  {
    "number": 54,
    "expected_output": """No Syntax Error""",
    "code": """start(){
    pass(i = 0; i += 1; i < 3){
        serve i;
    }
}"""
  },
  {
    "number": 55,
    "expected_output": """Syntax analysis not performed due to lexical errors:

Error at line 4 col 5 - Invalid Lexeme: Invalid delimiter for reserved word 'repeat'""",
    "code": """piece of x = 3;

start(){
    repeat[x < 5]{
        serve x;
    }
}"""
  },
  {
    "number": 56,
    "expected_output": """No Syntax Error""",
    "code": """table of Item = [
    piece of price;
];

Item of i = [
    price = 50;
];

start(){
    serve i:price + 10;
}"""
  },
  {
    "number": 57,
    "expected_output": """Syntax analysis not performed due to lexical errors:

Error at line 1 col 1 - Invalid Lexeme: Invalid delimiter for reserved word 'start'""",
    "code": """start[]{
    serve 0;
}"""
  },
  {
    "number": 58,
    "expected_output": """No Syntax Error""",
    "code": """prepare piece of inc(piece of x){
    serve x + 1;
}

start(){
    serve inc(3);
}"""
  },
  {
    "number": 59,
    "expected_output": """No Syntax Error""",
    "code": """piece of x = 5;
sip of y = 2.5;

prepare chars of makeText(piece of a, sip of b){
    serve tochars(a + topiece(b));
}

start(){
    serve makeText(x, y);
}"""
  },
  {
    "number": 60,
    "expected_output": """Syntax Error: Unexpected ':' at line 2, col 16. Expected '%', '+', '-', '*', '/', '==', '!=', '>=', '<=', '<', '>', ';'.""",
    "code": """start(){
    serve x + 1: 2;
}"""
  },
  {
    "number": 61,
    "expected_output": """No Syntax Error""",
    "code": """piece[] of array = [0,1,2];
piece[] of integers = [1,2,3];
flag of enabled = up;
start(){
bill("flag is: " + tochars(2 - size(array) > integers[0] and enabled == up));
}"""
  },
  {
    "number": 62,
    "expected_output": """Syntax Error: Unexpected 'piece_lit' at line 1, col 23. Expected 'id', 'append', 'sort', 'reverse', 'remove', '['.""",
    "code": """piece[] of integers = 1,2,3];
start(){
}"""
  },
  {
    "number": 63,
    "expected_output": """Syntax Error: Unexpected 'tochars' at line 2, col 19. Expected '+', ')'.""",
    "code": """start(){
bill("flag is: "  tochars(2));
}"""
  },
  {
    "number": 64,
    "expected_output": """Syntax Error: Unexpected ')' at line 2, col 16. Expected 'bill', 'take', 'copy', 'cut', 'tochars', 'chars_lit', 'id', '('.""",
    "code": """start(){
another = bill() += 23;
}"""
  },
  {
    "number": 65,
    "expected_output": """Syntax Error: Unexpected 'piece_lit' at line 2, col 6. Expected 'bill', 'take', 'copy', 'cut', 'tochars', 'chars_lit', 'id', '('.""",
    "code": """start(){
bill(0-array + 2);
}"""
  },
  {
    "number": 66,
    "expected_output": """No Syntax Error""",
    "code": """start(){
bill(tochars(topiece("32")-topiece(cut(12.56,2.0))));
}"""
  },
  {
    "number": 67,
    "expected_output": """Syntax Error: Unexpected ')' at line 2, col 26. Expected '%', '+', '-', '*', '/', '==', '!=', '>=', '<=', '<', '>'.""",
    "code": """start(){
pass(a = 3; a-=1; a and 0){
}
}"""
  },
  {
    "number": 68,
    "expected_output": """No Syntax Error""",
    "code": """start() {
  menu(1) { 
    choice 1: rand(); stop; 
    choice 2: size(a); stop;
  }
}"""
  },
  {
    "number": 69,
    "expected_output": """Syntax Error: Unexpected 'piece_lit' at line 1, col 33. Expected '*', '/', '%', '+', '-', ',', ';'.""",
    "code": """start() { piece of exprInit = 1 2; }"""
  },
  {
    "number": 70,
    "expected_output": """Syntax Error: Unexpected ';' at line 1, col 35. Expected 'id'.""",
    "code": """start() { tableType of m = field: ; }"""
  },
  {
    "number": 71,
    "expected_output": """Syntax Error: Unexpected '+' at line 1, col 135. Expected ']'.""",
    "code": """start() { piece[] of arr = [5,3,8,4,2]; piece of n = size(arr); pass(i=0; i+=1; i<n) { pass(j=0; j+=1; j<n-(1)) { check(arr[j] > arr[j+1]) { piece of temp = arr[j]; arr[j] = arr[j+1]; arr[j+1] = temp; } } } serve [arr]; }"""
  },
  {
    "number": 72,
    "expected_output": """No Syntax Error""",
    "code": """start() {
    piece[] of arr = [64,25,12,22,11];
    piece of n = size(arr);

    pass(i=0; i+=1; i<n-(1)) {
        piece of minIndex = i;
        piece of temp;
        pass(j=i+1; j+=1; j<n) {
            check(arr[j] < arr[minIndex]) {
                minIndex = j;
            }
        }
        temp = arr[minIndex];
        arr[minIndex] = arr[i];
        arr[i] = temp;
    }
    serve [arr];
}"""
  },
  {
    "number": 73,
    "expected_output": """Syntax Error: Unexpected '+' at line 10, col 18. Expected ']'.""",
    "code": """start() {
    piece[] of arr = [12,11,13,5,6];
    piece of n = size(arr);

    pass(i=1; i+=1; i<n) {
        piece of key = arr[i];
        piece of j = i-(1);

        repeat(j>=0 and arr[j] > key) {
            arr[j+1] = arr[j];
            j -= 1;
        }
        arr[j+1] = key;
    }
    serve [arr];
}
"""
  },
  {
    "number": 74,
    "expected_output": """No Syntax Error""",
    "code": """start() {
    piece[] of arr = [2,4,6,8,10];
    piece of target = 6;
    piece of n = size(arr);

    pass(i=0; i+=1; i<n) {
        check(arr[i] == target) {
            serve [i];
            stop;
        }
    }
    serve [-1]; # not found
}
"""
  },
  {
    "number": 75,
    "expected_output": """No Syntax Error""",
    "code": """start() {
    piece[] of arr = [1,2,3,4,5,6,7,8,9];
    piece of target = 7;
    piece of low = 0;
    piece of high = size(arr)-(1);

    repeat(low <= high) {
        piece of mid = (low + high) / 2;
        check(arr[mid] == target) {
            serve [mid];
            stop;
        }
        alt(arr[mid] < target) {
            low = mid + 1;
        }
        instead {
            high = mid - 1;
        }
    }
    serve [-1];
}
"""
  },
  {
    "number": 76,
    "expected_output": """No Syntax Error""",
    "code": """start() {
    piece of n = 5;
    piece of result = 1;

    pass(i=1; i+=1; i<=n) {
        result *= i;
    }
    serve [result];
}"""
  },
  {
    "number": 77,
    "expected_output": """Syntax Error: Unexpected '-' at line 6, col 23. Expected ']'.""",
    "code": """start() {
    piece of n = 10;
    piece[] of fib = [0,1];

    pass(i=2; i+=1; i<n) {
        fib[i] = fib[i-(1)] + fib[i-(2)];
    }
    serve [fib];
}
"""
  },
  {
    "number": 78,
    "expected_output": """No Syntax Error""",
    "code": """start() {
    piece of a = 48;
    piece of b = 18;

    repeat(b != 0) {
        piece of temp = b;
        b = a % b;
        a = temp;
    }
    serve [a];
}"""
  },
  {
    "number": 79,
    "expected_output": """No Syntax Error""",
    "code": """start() {
    piece of n = 29;
    flag of isPrime = up;

    pass(i=2; i+=1; i*i <= n) {
        check(n % i == 0) {
            isPrime = down;
            stop;
        }
    }
    serve [isPrime];
}
"""
  },
  {
    "number": 80,
    "expected_output": """No Syntax Error""",
    "code": """prepare piece[] of mergeSort(piece[] of arr) {
    piece of n;
    piece of mid;
    piece of i;
    piece[] of left;
    piece[] of right;
    piece[] of sortedLeft;
    piece[] of sortedRight;
    piece[] of result;

    n = size(arr);

    check(n <= (1)) {
        serve [arr];
    }

    mid = n / (2);
    left = [];
    right = [];

    # copy left half
    pass(i=0; i+=1; i<mid) {
        append(left, arr[i]);
    }

    # copy right half
    pass(i=mid; i+=1; i<n) {
        append(right, arr[i]);
    }

    sortedLeft = mergeSort(left);
    sortedRight = mergeSort(right);

    result = merge(sortedLeft, sortedRight);
    serve [result];
}

prepare piece[] of merge(piece[] of left, piece[] of right) {
    piece of i;
    piece of j;
    piece[] of merged;

    i = (0);
    j = (0);
    merged = [];

    pass(k=0; k+=1; k<size(left)+size(right)) {
        check(i < size(left) and (j >= size(right) or left[i] <= right[j])) {
            append(merged, left[i]);
            i += (1);
        }
        alt(j < size(right)) {
            append(merged, right[j]);
            j += (1);
        }
    }
    serve [merged];
}

start() {
    piece[] of arr;
    piece[] of sorted;

    arr = [38,27,43,3,9,82,10];
    sorted = mergeSort(arr);
    serve [sorted];
}
"""
  },
  {
    "number": 81,
    "expected_output": """Syntax Error: Unexpected ';' at line 6, col 22. Expected '='.""",
    "code": """piece of x = 2;

table of Food = [piece of qty;];

start(){
  Food of hotdog = [a;];
    
  bill();
}"""
  },
  {
    "number": 82,
    "expected_output": """Syntax analysis not performed due to lexical errors:

Error at line 2 col 3 - Invalid Lexeme: Invalid delimiter for reserved word 'prepare'""",
    "code": """start(){
  prepare;){}
}"""
  },
  {
    "number": 83,
    "expected_output": """Syntax analysis not performed due to lexical errors:

Error at line 1 col 1 - Invalid Lexeme: Invalid delimiter for reserved word 'prepare'""",
    "code": """prepare(){}
start(){}"""
  },
  {
    "number": 84,
    "expected_output": """Syntax Error: Unexpected ';' at line 1, col 13. Expected '[', 'id'.""",
    "code": """iwag of a = ;
start(){}"""
  },
  {
    "number": 85,
    "expected_output": """Syntax Error: Unexpected 'piece_lit' at line 2, col 14. Expected 'id', 'sqrt', 'rand', 'tosip', 'sip_lit', '('.""",
    "code": """piece of a; 
sip of b = ((3+5*2) and ) 5>10);
table of a = [
  piece of x;
];
start(){} 
}"""
  },
  {
    "number": 86,
    "expected_output": """Syntax Error: Unexpected 'piece' at line 1, col 14. Expected 'topiece', 'size', 'search', 'fact', 'pow', 'piece_lit', 'id', '('.""",
    "code": """piece of a = piece
start(){}"""
  },
  {
    "number": 87,
    "expected_output": """Syntax Error: Unexpected ':' at line 1, col 10. Expected '[', 'id'.""",
    "code": """a of a = :
start(){}"""
  },
  {
    "number": 88,
    "expected_output": """Syntax Error: Unexpected 'id' at line 3, col 12. Expected 'piece_lit', 'chars_lit'.""",
    "code": """start(){
  menu(a){
    choice a:a:a:a:
  }
}"""
  },
  {
    "number": 89,
    "expected_output": """Syntax Error: Unexpected ':' at line 22, col 34. Expected ',', ']'.""",
    "code": """  
table of Student = [
  piece of Name;
    chars of Age;
];

start() {
  Student of Student1 = [
      Name = 1;
        Age = "Hello";
    ];
    
    Student of Student2 = [
      Name = 2;
        Age = "World";
    ];
    
  Student[] of Class = [
    
    ];
    
    chars[] of Class1 = [Student1:Name, Student1:Age];
    
  serve 0;
}"""
  },
  {
    "number": 90,
    "expected_output": """No Syntax Error""",
    "code": """start() {
  piece of a = 5/2 + 13;
}"""
  },
  {
    "number": 91,
    "expected_output": """Syntax Error: Unexpected 'sip_lit' at line 2, col 18. Expected 'topiece', 'size', 'search', 'fact', 'pow', 'piece_lit', 'id', '('.""",
    "code": """start() {
  piece of a = ((1.2/6) + bill());
}"""
  },
  {
    "number": 92,
    "expected_output": """No Syntax Error""",
    "code": """piece[] of array = [0,1,2];
piece[] of integers = [1,2,3];
flag of enabled = up;
start(){
bill("flag is: " + tochars(2 - size(array) > integers[0] and enabled == up));
}"""
  },
  {
    "number": 93,
    "expected_output": """No Syntax Error""",
    "code": """start() {
piece of x = 5;
piece of y = (x + 3);
ans = tochars(y);
bill(ans);
}"""
  },
  {
    "number": 94,
    "expected_output": """No Syntax Error""",
    "code": """sip of pi = 3.14;

prepare sip of circumference(piece of r){
        serve 2*pi*r;
}

start(){
        sip of c = circumference(3);
        chars of ans = tochars(c);
        bill("The answer is: " + ans);
}"""
  },
  {
    "number": 95,
    "expected_output": """Syntax Error: Unexpected 'piece_lit' at line 2, col 15. Expected 'id', 'sqrt', 'rand', 'tosip', 'sip_lit', '('.""",
    "code": """start(){
  sip of c = (1 < 3 == 2);
}"""
  },
  {
    "number": 96,
    "expected_output": """Syntax Error: Unexpected 'piece' at line 1, col 7. Expected ')'.""",
    "code": """start(piece of x){
        x = 1;
}"""
  },
  {
    "number": 97,
    "expected_output": """Syntax Error: Unexpected 'prepare' at line 2, col 9. Expected 'piece', 'chars', 'sip', 'flag', 'id', 'append', 'bill', 'copy', 'cut', 'fact', 'matches', 'pow', 'rand', 'remove', 'reverse', 'search', 'size', 'sort', 'sqrt', 'take', 'tochars', 'topiece', 'tosip', 'check', 'menu', 'pass', 'repeat', 'order', 'serve', '}'.""",
    "code": """start(){
        prepare piece of a(){}
}"""
  },
  {
    "number": 98,
    "expected_output": """No Syntax Error""",
    "code": """start(){
        menu(a){
            choice 1:
        choice 2:
                order{} repeat (a > 0);
    }
}"""
  },
  {
    "number": 99,
    "expected_output": """No Syntax Error""",
    "code": """start(){
        order{
      menu(a){
          choice 1:
              next;
              serve 1;
          choice 2:
              order{} repeat (a > 0);
      }
    } repeat(a > 3);
}"""
  },
  {
    "number": 100,
    "expected_output": """Syntax Error: Unexpected 'pow' at line 1, col 12. Expected 'id', 'sqrt', 'rand', 'tosip', 'sip_lit', '('.""",
    "code": """sip of a = pow(x,2)/sqrt(cut(y,1,3)) + fact(n);
start(){}"""
  },
  {
    "number": 101,
    "expected_output": """Syntax Error: Unexpected 'piece_lit' at line 3, col 16. Expected 'id', 'sqrt', 'rand', 'tosip', 'sip_lit', '('.""",
    "code": """start() {
    piece of x = 12  + 13 ;
    sip of y = 123;
    serve 0
}"""
  },
  {
    "number": 102,
    "expected_output": """No Syntax Error""",
    "code": """prepare piece of add2(piece of y) {
    serve y+2;
}

start() {
        piece of xd = add2(12) + add2(13);
    bill(tochars(xd));
}"""
  },
  {
    "number": 103,
    "expected_output": """No Syntax Error""",
    "code": """start() {
  repeat(x < 10) {
    x = x + 1;
    next;
    x = x + 999;  
    # comment ko
  }
}
"""
  },
  {
    "number": 104,
    "expected_output": """Syntax Error: Unexpected '=' at line 2, col 7. Expected ']'.""",
    "code": """start() {
  a[0 = 1;
}
"""
  },
  {
    "number": 105,
    "expected_output": """Syntax Error: Unexpected ';' at line 2, col 34. Expected 'of', '[', ':', '=', '+=', '-=', '*=', '/=', '%=', '('.""",
    "code": """prepare piece of serving () {
        serving of server; server; }

start() {
}
"""
  },
  {
    "number": 106,
    "expected_output": """No Syntax Error""",
    "code": """start() {
  person:age = 19;
  person:name = "Floyd";
}
"""
  },
  {
    "number": 107,
    "expected_output": """Syntax Error: Unexpected 'start' at line 8, col 1. Expected ';'.""",
    "code": """table of person = [
        piece of age;
    chars of name;

]


start() {}"""
  },
  {
    "number": 108,
    "expected_output": """Syntax Error: Unexpected 'id' at line 2, col 23. Expected '*', '/', '%', '+', '-', ',', ';'.""",
    "code": """start() {
  piece of badval = 1 value;
}"""
  },
  {
    "number": 109,
    "expected_output": """Syntax Error: Unexpected ';' at line 2, col 74. Expected '*', '/', '%', '+', '-', '==', '!=', '>=', '<=', '<', '>'.""",
    "code": """start() {
  flag of expr = 1 - 23 > 12  and (up and down) * 12 * 1 * 2 % 12 / (1/2);
}
"""
  },
  {
    "number": 110,
    "expected_output": """Syntax Error: Unexpected ';' at line 2, col 27. Expected 'topiece', 'size', 'search', 'fact', 'pow', 'piece_lit', 'id', '('.""",
    "code": """start() {
  piece of badexpr = 1 -  ;
}"""
  },
  {
    "number": 111,
    "expected_output": """No Syntax Error""",
    "code": """prepare piece of add1() {
  x = x + 1;
}

prepare piece of add2() {
  add1();
  add1();
}

start() {
  x = 0;
  add2();
}
"""
  },
  {
    "number": 112,
    "expected_output": """Syntax Error: Unexpected '{' at line 3, col 3. Expected 'id', 'append', 'bill', 'copy', 'cut', 'fact', 'matches', 'pow', 'rand', 'remove', 'reverse', 'search', 'size', 'sort', 'sqrt', 'take', 'tochars', 'topiece', 'tosip', 'check', 'menu', 'pass', 'repeat', 'order', 'serve', '}'.""",
    "code": """start() {
  x = 1;
  {
    y = x + 2;
  }
}
"""
  },
  {
    "number": 113,
    "expected_output": """No Syntax Error""",
    "code": """start() {
  flag of ok = (a + b * 2) >= (c - 1) and not (d == 0) or e < 5;
}
"""
  },
  {
    "number": 114,
    "expected_output": """Syntax Error: Unexpected 'chars' at line 6, col 3. Expected 'id', 'append', 'bill', 'copy', 'cut', 'fact', 'matches', 'pow', 'rand', 'remove', 'reverse', 'search', 'size', 'sort', 'sqrt', 'take', 'tochars', 'topiece', 'tosip', 'check', 'menu', 'pass', 'repeat', 'order', 'serve', '}'.""",
    "code": """start() {
  person of floy;
  floy:age = 19;
  floy:age = floy:age + 1;
  isAdult = floy:age >= 18;
  chars of x = tochars(isAdult); 
  bill(x);
}
"""
  },
  {
    "number": 115,
    "expected_output": """No Syntax Error""",
    "code": """start() {
  pass( x = 0; x+=1 ; x>1) {
    sum = x + y + z;
  }
}
"""
  },
  {
    "number": 116,
    "expected_output": """Syntax Error: Unexpected 'flag_lit' at line 4, col 10. Expected 'id'.""",
    "code": """start() {
  repeat(true) {
    x = x + 1;
    pass(up) { stop; }
  }
}
"""
  },
  {
    "number": 117,
    "expected_output": """No Syntax Error""",
    "code": """start() {
  x = 0;
  order {
    x = x + 2;
    y = x * 3;
    x+=1;
  } repeat(x < 6);
}
"""
  },
  {
    "number": 118,
    "expected_output": """Syntax Error: Unexpected 'id' at line 5, col 12. Expected '('.""",
    "code": """start() {
  order {
          piece of x = 1;
    x = x + 1;
  } repeat x < 3;
}
"""
  },
  {
    "number": 119,
    "expected_output": """Syntax Error: Unexpected 'pow' at line 2, col 28. Expected 'id', 'sqrt', 'rand', 'tosip', 'sip_lit', '('.""",
    "code": """start() {
  sip of r = sqrt(9),  p = pow(2, 8);
  sip of n = rand();
}
"""
  },
  {
    "number": 120,
    "expected_output": """Syntax Error: Unexpected 'id' at line 6, col 23. Expected '+', '==', '!=', '>=', '<=', '<', '>', ';'.""",
    "code": """table of animal = [ chars of sound; ];

start() {
        animal of pig;
    chars of cat = "meow";
    pig:sound = "cat" cat;
}"""
  },
  {
    "number": 121,
    "expected_output": """Syntax Error: Unexpected '}' at line 3, col 1. Expected ';'.""",
    "code": """start(){
      bill("Hello World")
}"""
  },
  {
    "number": 122,
    "expected_output": """Syntax Error: Unexpected 'piece_lit' at line 2, col 20. Expected '=', ',', ';'.""",
    "code": """start(){
        piece of x 10;
}"""
  },
  {
    "number": 123,
    "expected_output": """Syntax Error: Unexpected 'piece_lit' at line 2, col 24. Expected '*', '/', '%', '+', '-', ',', ';'.""",
    "code": """start(){
        piece of z = 5 10;
}"""
  },
  {
    "number": 124,
    "expected_output": """Syntax Error: Unexpected 'id' at line 2, col 9. Expected 'of', '[', ':', '=', '+=', '-=', '*=', '/=', '%=', '('.""",
    "code": """start() {
    int sum = 24 + 26;
        bill(tochars(sum));
}
"""
  },
  {
    "number": 125,
    "expected_output": """No Syntax Error""",
    "code": """start() {
piece of xx = 24 + 26;
        bill(tochars(sum));
}"""
  },
  {
    "number": 126,
    "expected_output": """No Syntax Error""",
    "code": """start(){     
       check (input > 0){
            bill("Number is positive");
        } alt (input < 0){
            bill("Number is negative");
        } instead{
            bill("Number is zero");
        }
}"""
  },
  {
    "number": 127,
    "expected_output": """No Syntax Error""",
    "code": """start(){     
       check (input > 0){
            bill("Number is positive");
        } alt (input < 0){
            bill("Number is negative");
        } instead{
            bill("Number is zero");
        }
}"""
  },
  {
    "number": 128,
    "expected_output": """No Syntax Error""",
    "code": """start(){
        piece of z = 5 + 10;
}"""
  },
  {
    "number": 129,
    "expected_output": """Syntax Error: Unexpected 'EOF' at line 1, col 16. Expected 'piece', 'chars', 'sip', 'flag', 'table', 'id', 'prepare', 'start'.""",
    "code": """piece of x = 42; """
  },
  {
    "number": 130,
    "expected_output": """Syntax Error: Unexpected 'remove' at line 5, col 1. Expected 'piece', 'chars', 'sip', 'flag', 'table', 'id', 'prepare', 'start'.""",
    "code": """piece[] of nums = [1, 2, 3];
piece of num = 1;


remove([1, 2, 3], 1);
"""
  },
  {
    "number": 131,
    "expected_output": """Syntax analysis not performed due to lexical errors:

Error at line 2 col 2 - Invalid Lexeme: Invalid delimiter for reserved word 'serve'""",
    "code": """start(){
        serve;
}"""
  },
  {
    "number": 132,
    "expected_output": """No Syntax Error""",
    "code": """start(){
        piece of x = 10, b = 5;
}"""
  },
  {
    "number": 133,
    "expected_output": """Syntax Error: Unexpected 'EOF' at line 5, col 2. Expected 'piece', 'chars', 'sip', 'flag', 'table', 'id', 'prepare', 'start'.""",
    "code": """table of Vector3= [
     piece of x;
     piece of y;
     piece of z;
];
"""
  },
  {
    "number": 134,
    "expected_output": """No Syntax Error""",
    "code": """piece of a;

start(){
        sip of a, b, c;
        piece of a;
}
"""
  },
  {
    "number": 135,
    "expected_output": """Syntax Error: Unexpected '+=' at line 1, col 7. Expected 'of', '['.""",
    "code": """three += one;"""
  },
  {
    "number": 136,
    "expected_output": """Syntax Error: Unexpected '+' at line 3, col 11. Expected 'of', '[', ':', '=', '+=', '-=', '*=', '/=', '%=', '('.""",
    "code": """start(){
        piece of num = 2, c=3, x=10, y=5;
        x + c * y
}"""
  },
  {
    "number": 137,
    "expected_output": """No Syntax Error""",
    "code": """start(){
        chars of name = "Tricia";
    bill("Hello" + name);
}"""
  },
  {
    "number": 138,
    "expected_output": """No Syntax Error""",
    "code": """
piece of number = 10;

start(){
order {
        bill("Enter a positive number: ");
 
} repeat (number > 0);
}"""
  },
  {
    "number": 139,
    "expected_output": """Syntax Error: Unexpected '=' at line 2, col 8. Expected 'of', '['.""",
    "code": """piece of candy = 1;
peanut = 0;

start(){
check(candy == 1){
} alt(candy == 2){
 }
}"""
  }
]