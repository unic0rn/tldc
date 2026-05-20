tl;dc
================

## about

This is a work in progress and it'll likely stay that way for a while. It's just another agentic AI CLI tool, with a focus on xAI's response API. Support for stateless APIs is also possible, as evidenced by Ollama support - that one is borked for now though, see below.

## status / roadmap

* xAI/Grok works fine, but grok-code-fast-1 is gone, and with it the main reason to use Grok for coding: it was inexpensive.
* Ollama works fine (currently hardcoded temperature=0.6, keep that in mind when using Gemma 4).
* Limited tools are available to the AI. AI **cannot** leave current directory and **cannot** execute shell commands. This is by design. Available tools:
    * listing files and directories
    * reading a file
    * writing a file
    * web search
    * fetching websites as markdown

## manual

* xAI configuration:
```bash
tldc models add grok-code-fast-1 xai '{"api_key": "<API_KEY>"}'
tldc models set grok-code-fast-1
```
* Ollama configuration:
```bash
tldc models add qwen3.5:35b-a3b-coding-nvfp4 ollama '{"url": "http://127.0.0.1:11434"}'
tldc models add qwen3.5:27b-coding-nvfp4
tldc models set qwen3.5:27b-coding-nvfp4
```
* For the list of available commands, just run `tldc` without parameters.
* Active model is a global setting.
* Context refers to the current working directory. It stores things like message history.

## too lazy; didn't code
_aka what's with the name_

The best way to code is as follows:
* plan what needs to be done
* tell someone else to do it
* grab a coffee
* code review
* profit

You may think that _someone else_ is a bottleneck.
You may think _I'll better do it myself_.
But when it comes to AI, even if it's not as good as you, it **is** faster.

**Orders of magnitude faster**.

So even if you have to repeat those steps several times to get the end result you're after, you're still saving a lot of ~~time~~ money.

And everyone likes money.