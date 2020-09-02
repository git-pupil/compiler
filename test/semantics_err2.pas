program example(input,output);
var x,y:integer;
function test : integer;
begin
end;
function gcd(a,b:integer):integer;
var z : real;
begin
gcd(a, z); {parameters type error}
gcd;  {need parameters}
test(a); {do not need parameters}
x(a);  {not be a function}
if b then gcd:=a {if A then B}
else gcd:=gcd(b); {function parameters wrong}
while a do {while must be boolean}
a := 2;
for a := 0 to 2.5 do {must be integer}
a := a;
end;
begin
read(x, y);
write(gcd(x, y))
end.