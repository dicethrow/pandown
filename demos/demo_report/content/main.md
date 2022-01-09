
---
title: Some title
documentclass: paper
panflute-filters: [ignore_comments, assemble_parts]
panflute-path: '~/Documents/Uploads/filters'
starting_dir: "~/Documents/Uploads/content"
...

# heading level 1 in /main.md

**paragraph** in /main.md

note the things in **parts** can be .md files, or *directories* which contain a mian.md

![alt text](./panasonic_amorton_indoor_list.png)

ababa!!

well let's consider this algorithm

```python
def mainko(bozo):
	return "hungry"
```

as well as this

```c
int mainko(int bozo){
	return ERROR_UNDEF;
}
```

## heading level 2
aaa

### heading level 3
bbb

``` parts
my_key_1: my_value_1
my_key_2: my_value_2
---
a_outerfolder
b_outerfolder
c_outerfolder
d_outerfolder
```


``` comment
quote: Simplicity is the ultimate sophistication.
who: Leonardo da Vinci
---
a_intro
b_aaa
c_dee
d_doo
```

# another top level heading 

here's a copy-pasted thing of the parts - does it work?

``` parts
my_key_1: my_value_1
my_key_2: my_value_2
---
a_outerfolder
b_outerfolder
c_outerfolder
d_outerfolder
```
