program example(input, output);
    var x, y : real ;
    p, q : integer ;
    z : integer ;
    function myfunction ( var c, d : real; e, f : integer) : integer ;
        begin
            c := d;
            myfunction := e
        end;
    begin
        z := myfunction(x, y, p , q)
    end.