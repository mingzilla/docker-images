this is created to mirror ollama-qwen3pt5_9b, which is fantastic
now what's missing is, 
- this project needs to support 2 models: gemma4:e4b, gemma4:26b, see ollama-gemma4/readme.md
- i don't want to use ollama-gemma4/stop_clean_start.sh to wipe things out all the time
- if a model is downloaded to my machine, i don't want to waste half an hour to download it again
- but then at the same time i don't want a system to always download 2 models if only 1 is used
- i don't mind the 2 models running on different ports, that gives me the flexibility of running them at the same time or just run one
- this would be good because i want to potentially use claude code to launch sub-agents using a small model for small tasks
- potentially in the future if this works, i don't see why i can't launch ollama-qwen3pt5_9b on demand to do work

thoughts please