program example(input,output);
var x,y:integer; x,z : real; test4 : boolean; abs : array[0..4.5] of integer; abd : array[20..10] of integer; {wrong 3}
function gcd(a,b:integer):integer;
var abc : array[0..6] of integer;
begin
test := 1; {undifined id}
x := x or z; {cannot or 'real'}
x := 1.5; {int <- real}
z := 1 + 1.5; {real <- real}
a := (1 > 0); {error type}
test4 := test4 > 1;  {cannot compare}
test4 := test4 + 1; {cannot + }
test4 := x or z; {cannot or}
test4 := test4*test4; {cannot mulop}
z := not z; {cannot not}
z := uminus test4; {cannot uminus}
abc := 1; {wrong}
abc[1.2] := 1; {wrong}
if b then gcd:=a  { if A then B, a is bool}
else gcd:=gcd(b, a mod b)
end;
begin
read(x, y);
write(gcd(x, y))
end.