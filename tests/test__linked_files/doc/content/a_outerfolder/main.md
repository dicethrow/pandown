# Heading level 1 (should become 2) in content/a_outerfolder/main.md

Content below that heading in the markdown file

xxx change


let's see if this *mermaid* filter works. Should look like the example from https://github.com/raghur/mermaid-filter



``` mermaid
sequenceDiagram
    Alice->>John: Hello John, how are you?
    John-->>Alice: Great!
    
```

Now let's try another, this one from here: https://stackoverflow.com/questions/68561397/mermaid-syntax-error-on-trying-render-a-diagram-on-github-md-file

``` mermaid
sequenceDiagram
    autonumber
    Alice->>John: Hello John, how are you?
    loop Healthcheck
        John->>John: Fight against hypochondria
    end
    Note right of John: Rational thoughts!
    John-->>Alice: Great!
    John->>Bob: How about you?
    Bob-->>John: Jolly good!
```

This is a [link to demo doc 2](demo%20doc%202.pdf), clicking this link should open the file, which should be copied to the output folder.