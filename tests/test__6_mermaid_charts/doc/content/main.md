
---
title: Some title
subtitle: And a small subtitle
documentclass: paper
panflute-filters: [ignore_comments, assemble_parts,mermaid_charts, copy_linked_items]
...

# This is part one

## heading one in /main.md

Edit made on new os.

**paragraph** in /main.md

note the things in **parts** must be *directories* which contain a main.md. That main.md file may also have a **parts** section for including further files, etc.

![alt text](./spaceship.png)


# This is part two

## To do
- Closely match the appearance of my latex documents from a year ago
	- same border spacing
	- same structure, e.g. have an abstract/terminology/progress sections, bibliography/appendix etc
	- make top level headings as 'parts', e.g. part 1, part 2,


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

## heading level 2 in the .md
aaa

### heading level 3 in the .md
bbb

todo - make the key:value thing in parts be section parts to filenames, e.g. for abstract, progress, etc?
``` parts
a_outerfolder
b_outerfolder
c_outerfolder
d_outerfolder
```

<!-- 
``` comment
hello this is an ignorable comment
``` -->

# another top level heading 

here's a copy-pasted thing of the parts - does it work?
<!-- 
``` parts
my_key_1: my_value_1
my_key_2: my_value_2
---
a_outerfolder
b_outerfolder
c_outerfolder
d_outerfolder
``` -->
