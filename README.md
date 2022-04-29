# KS-shell
KEA-stream in simple shell

## using KS and KEA

- [KEA stream](https://github.com/KEA-corp/KEA-stream)
- [KEA interpreter](https://github.com/KEA-corp/simple-py)

## example

```c
KS $ 1, 0 >> and > print
0

KS $ 0 > $i
KS $ 5 > LOOP
KS $    $i + 1 > $i > print
KS $    END
1
2
3
4
5
```