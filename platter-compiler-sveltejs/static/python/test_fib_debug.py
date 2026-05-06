from tests.ga_compiler import run_compiler

code = r'''start(){
piece of N = 10, a = 0, b = 1, i = 0;
bill(tochars(N - 2));
bill("\n");
repeat(i < N - 2){
piece of c = a + b;
bill(tochars(i));
bill(" ");
a = b;
b = c;
i += 1;
}
}'''

result = run_compiler(code, [])
print('Output:')
print(result['output'])
print('---')
print('i values should be: 0 1 2 3 4 5 6 7')
