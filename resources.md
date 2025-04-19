# The Case For Resources

- Easy to expand MAS (just create some agent with some tools and they can immediately start working with other agents within the MAS)
- Creates inherent """communication""" protocol (not quite communication bc you can't reply you just tell others what to do [but we can create a comms protocol on top of this potentially])
- Improves accuracy and predicitability of results (explicitly ask for what you want)
- Smart caching (parameterised caching, and results-based caching [only cache good results])
- Can be expanded to include costs for actions (functions that use resources to create new resources), and therefore basic "bidding"
- Local KB can be implemented as resources that can only accessed by that agent
- Separation of concerns: agents, resources, actions, input, output, plan, execution are all separated nicely
- Allows you to pause and step through each step of the MAS
- Can utilise any agent/s (e.g. ag2 group chat, seq chat, single agent, non-LLM based agent, other framework as long as they can produce the resource)
- Evaluation and learning (potentially automatic, you can see the success rate of each function and find out where the point of failure is)
- Robust way of exploring the capabilities of the MAS (see what resources it knows about, and what actions it has explicitly defined)

# Plan

You define a request as an input and a desired output.

```
INPUT:

Topic(ID=1):
    About: "cats"

OUTPUT:

Sentence(ID=2):
    Descriptors:
        Capitalised
    Dependencies:
        Topic(ID=1)

Sentence(ID=3):

Sentence(ID=4):
    Dependencies:
        Combined(Sentence(ID=2), Sentence(ID=3))

<!-- The other resources were needed to compute Sentence(ID=4) but don't need to be returned -->
YIELD Sentence(ID=4)
```

The prompt equivalent is

```Write a sentence about cats in all caps and then combine it with another sentence about another topic```

The question becomes if you have generic functions like:

"Write a sentence on the topic: {topic}" -> {sentence}

"Capitalise this sentence {sentence}" -> {sentence}

"Capitalise the first letter of this sentence {sentence}" -> {sentence}

"Combine these sentences {sentence} and {sentence}" -> {sentence}

"Think of a topic to write about" -> {topic}

"Yield {resource}" -> {resource}

<!-- you will see what this is needed for later -->
"Assign {id} to {resource}" -> {resource(id={id})}

How can I generate a horn kb to guarantee it satisfies these dependencies?

And then use that to find the path of functions to call to satisfy the output from the begining input.

# Solution

## Func defs become:

"Write a sentence on the topic: {topic(id=1)}" -> {sentence(id=2)}

"Capitalise this sentence {sentence(id=2)}" -> {sentence(id=2)}

"Capitalise the first letter of this sentence {sentence(id=3)}" -> {sentence(id=3)}

"Combine these sentences {sentence(id=2)} and {sentence(id=3)}" -> {sentence(id=4)}

"Think of a topic to write about" -> {topic(id=any)} 
<!-- you don't even need this topic to have an id even though it gets passed into another func -->
<!-- bc we don't care how we get there -->

"Write a sentence on the topic {topic(id=any)}" -> {sentence(id=any)}

<!-- But you would need a way to sort of assign an id to the sentence -->
<!-- so we do this -->
"Assign {id=3} to {sentence(id=any)}" -> {sentence(id=3)}

## But kb needs to consider dependencies as in like order like you want to capitalise before combining

So you need to add some sort of dependency ordering. This easy to do. You just add a symbol for each descriptor until they are all resolved.

This looks like this in the kb:

<!-- descriptor dependency -->
Capitalised(id=2) => DescriptorsSatsified(id=2)

<!-- Combine Sentences Rule -->
<!-- NOTE: You don't need to have the topic in dependency because it is already handled -->
<!-- You only need to handle the descriptor dependencies because they just mutate -->
Sentence(id=2) & DescriptorsSatsified(id=2) & Sentence(id=3) => Sentence(id=4)

<!-- the reason you have DescriptorsSatsified is in case you need multiple descriptors e.g. -->
RemoveFirstLetter(id=2) & Capitalised(id=2) => DescriptorsSatsified(id=2)

## What if you want descriptor dependencies?

E.g. you want to satisfy the order of descriptors.

You can just put them in order.

Consider the sentence "hello WORLD"

Sentence(ID=3):
    Descriptors:
        RemoveCapitals
        FirstLetterCapitalised

becomes "Hello "

Sentence(ID=3):
    Descriptors:
        FirstLetterCapitalised
        RemoveCapitals

becomes "ello "

# Some Unknowns

## How do you handle iterables?

Maybe you get given a list of sentences. How would this look like to apply descriptors to each sentence in the list. I'm not sure, I think you would create some sort of iterable resource (e.g. sentences(id=1)) and then some sort of iter resource (sentence(id=iter1)) and it would rerun for each. Might get a bit dank but something to consider later I think but seems giga doable.


## Conditionals

### Conditional Descriptors

<!-- Something like this. -->
<!-- You would need some sort of parser for conditions tho -->
```
Sentence(ID=2):
    Descriptors:
        If WordCount > 1: 
            Capitalised
        Else:
            FirstLetterCapitalised
    Dependencies:
        Topic(ID=1)
```

### Conditional Resources

<!-- Idk why you want this or what it would look like -->

## Another Feature - CustomResources

Consider the original input:

```
INPUT:

Topic(ID=1):
    About: "cats"

OUTPUT:

Sentence(ID=2):
    Descriptors:
        Capitalised
    Dependencies:
        Topic(ID=1)

Sentence(ID=3):

Sentence(ID=4):
    Dependencies:
        Combined(Sentence(ID=2), Sentence(ID=3))

<!-- The other resources were needed to compute Sentence(ID=4) but don't need to be returned -->
YIELD Sentence(ID=4)
```

```Write a sentence about cats in all caps and then combine it with another sentence about another topic```

What if we wanted to do the same thing for dogs?

It would be the whole thing but replacing it with dogs.

To simplify this if the user plans on using the same functionality again and again they can define a "custom resouce"

Just replace the last line to specify the custom resource

```
YIELD Sentence(ID=4) as FancySentence
```

Then you can just ask for the custom resource with new params e.g. topic is now "dogs"

```
INPUT:

Topic(ID=1):
    About: "dogs"

OUTPUT:

FancySentence(ID=2):
    Dependencies:
        Topic(ID=1)

YIELD FancySentence(ID=2)
```

And it just works.

Now you could simplify this by having separate IDs for each resource. E.g. each resource type starts at 1, not shared

```
INPUT:

Topic(ID=1):
    About: "dogs"

OUTPUT:

FancySentence(ID=1):
    Dependencies:
        Topic(ID=1)

YIELD FancySentence(ID=1)
```

Now since they are both ID=1, if there are no ID=2s, we can assume there is only one of these resources.

```
INPUT:

Topic():
    About: "dogs"

OUTPUT:

FancySentence():
    Dependencies:
        Topic()

YIELD FancySentence()
```

## Another Feature - PromptBasedDescriptors

What if you want to make a simple descriptor that could be solved by simple prompt.

Like what if you wanted to make the sentence in all caps but that descriptor tool wasn't available. You could just do this:

```
INPUT:

Topic(ID=1):
    About: "cats"

OUTPUT:

Sentence(ID=1):
    Descriptors:
        PromptDescriptor(name="Capitalised")
            "Capitalise this sentence: {X}"
    Dependencies:
        Topic(ID=1)

YIELD Sentence(ID=1) as CapitalisedSentence
```

You could go one step further and create some sort of method for defining these sort of descriptor callbacks (maybe like a math based descriptor, e.g. SimplifiedExpression, or CorrectToNDecimals(n=2)).

## Another Feature - ParameritisedDescriptors

Imagine you want to remove the last 3 letters of the sentence, and you have a tool that can remove the last n letters of the sentence. How do you tell the descriptor that it needs 3? Like so:

```
INPUT:

Topic(ID=1):
    About: "cats"

<!-- Define the param as a resource -->
Integer(ID=1):
    Value: 3

OUTPUT:

Sentence(ID=1):
    Descriptors:
        PromptDescriptor(name="Capitalised")
            "Capitalise this sentence: {X}"

        <!-- The difference between a descriptor and a resource is that they can only be called one way -->
        <!-- So we can define it inline like this -->
        <!-- We can't do that for the sentences, like Sentence(topic=Topic(ID=1)) 
        because there might be otherwise to generate a sentence that don't require a topic e.g reading from a file. -->
        RemovedLastNLetters(n=Integer(ID=1))
            
    Dependencies:
        Topic(ID=1)

YIELD Sentence(ID=1) as CapitalisedSentence
```

## Another Feature - Named Params

It might be confusing to see the Integer resource, what does it represent? So instead of defining ID=1 we can give it a descriptive name instead. You can even mix and match names and numbers if you can't think of a good name for a resource.

