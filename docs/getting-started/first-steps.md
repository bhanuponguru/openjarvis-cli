# First Steps

Now that OpenJarvis is installed and configured, let's explore what you can do with it.

---

## Interactive Chat

The default mode is an interactive chat session:

```bash
openjarvis
```

Type your questions and press Enter. Type `exit` or `quit` to stop.

---

## Example Sessions

### Basic Math

```
> What is 25% of 480?

  routing: generalist → math → tool_use
  routing: tool_use → math → generalist

25% of 480 is 120.
```

**What happened:**
1. Generalist routed to math specialist
2. Math specialist used the `calculate` tool
3. Result returned to generalist for final answer

### Web Search

```
> What is the current population of Japan?

  routing: generalist → knowledge → tool_use
  routing: tool_use → knowledge → generalist

Japan's current population is approximately 125.7 million people.
```

**What happened:**
1. Generalist routed to knowledge specialist
2. Knowledge specialist used `web_search` tool
3. Result synthesized and returned

### Code Generation

```
> Write a Python function to check if a number is prime

  routing: generalist → code
  routing: code → generalist

Here's a function to check if a number is prime:

```python
def is_prime(n):
    """
    Check if a number is prime.
    
    Args:
        n: The number to check
        
    Returns:
        True if n is prime, False otherwise
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True
```

This function handles edge cases and uses an optimized algorithm.
```

**What happened:**
1. Generalist recognized this as a code task
2. Routed to code specialist
3. Code specialist generated the function with documentation

### Multi-Step Reasoning

```
> Find the GDP of Germany and France, then tell me which is higher

  routing: generalist → knowledge → tool_use
  routing: tool_use → knowledge → generalist

Germany's GDP: ~$4.3 trillion
France's GDP: ~$3.0 trillion

Germany has the higher GDP, exceeding France by approximately $1.3 trillion.
```

**What happened:**
1. Knowledge specialist searched for both GDPs
2. Returned data to generalist
3. Generalist compared and synthesized the answer

### Creative Writing

```
> Write a haiku about AI

  routing: generalist → creative
  routing: creative → generalist

Silicon minds think
Learning patterns, finding truth
Future is now here
```

**What happened:**
1. Generalist recognized creative writing task
2. Routed to creative specialist
3. Creative specialist composed the haiku

---

## Understanding Routing

### Routing Indicators

When you see:

```
  routing: generalist → math
```

This means the generalist decided to route your request to the math specialist.

```
  routing: math → tool_use
```

This means the math specialist delegated to the tool specialist to execute a calculation.

```
  routing: tool_use → math → generalist
```

This shows the complete return path: tool result went back to math, then math's answer went back to generalist.

### Why Routing Matters

Different models/specialists have different strengths:

- **Math specialists** are better at calculations (configured with low temperature for precision)
- **Code specialists** are better at generating code (may use models like CodeLlama)
- **Creative specialists** are better at writing (configured with high temperature for variety)
- **Knowledge specialists** are better at facts (configured to use search tools)

By routing to the right specialist, you get better results than using a single general-purpose model.

---

## Built-In Tools

OpenJarvis has 29 built-in tools that specialists can use automatically. You don't need to call them explicitly — just ask naturally.

### Web Tools

```
> Search for the latest research on transformers
> Fetch the content from https://example.com
> Make an HTTP POST request to this API endpoint
```

### Math Tools

```
> Calculate 15.5 * 234 + 67
> Solve for x: 2x + 5 = 15
> Convert 50 miles to kilometers
```

### File Tools

```
> Read the file config.yaml
> Write "Hello World" to output.txt
> List all files in the current directory
> Does the file data.json exist?
```

### Code Execution

```
> Run this Python code: print([x**2 for x in range(10)])
> Execute this shell command: ls -la
```

⚠️ **Security Warning:** Code execution runs on your machine. Only execute code you trust.

### Date & Time Tools

```
> What's the current time?
> What's today's date?
> How many days between 2024-01-01 and 2024-12-31?
> Add 30 days to today's date
```

### Text Processing

```
> Count the words in this text: [paste text]
> Extract JSON from this string: [paste string]
> Format this JSON nicely: {"a":1,"b":2}
```

### System Tools

```
> What's the value of the HOME environment variable?
> What's my system information?
```

### Memory Tools

```
> Save a note called "reminder": Call John at 3 PM
> Get the note "reminder"
> List all my saved notes
```

See [Built-in Tools](../tools/overview.md) for the complete reference.

---

## Command-Line Usage

### Piping Queries

```bash
# Run a single query and exit
echo "What is 2 + 2?" | openjarvis
```

### Custom Config File

```bash
# Use a different configuration
openjarvis --config production.yaml
```

### Streaming Mode

```bash
# Enable real-time streaming output
openjarvis --stream
```

### Verbose Logging

```bash
# See detailed logs (useful for debugging)
openjarvis --verbose
```

---


---

## Customization

### Using Different Models

Edit `specialists.yaml` to change models:

```yaml
code:
  model: "codellama"  # Change to "llama3" or "gpt-4"
  base_url: "http://localhost:11434/v1"
```

### Mixing Providers

Use different providers for different specialists:

```yaml
generalist:
  base_url: "https://api.openai.com/v1"  # OpenAI
  model: "gpt-4o-mini"

specialists:
  code:
    base_url: "http://localhost:11434/v1"  # Ollama (local)
    model: "codellama"
  
  knowledge:
    base_url: "https://api.groq.com/v1"  # Groq (fast)
    model: "llama-3.1-70b"
```

### Adjusting Temperature

Control creativity vs precision:

```yaml
math:
  temperature: 0.1  # Very precise, deterministic

creative:
  temperature: 0.9  # Very creative, diverse
```

- **Low temperature (0.1-0.3):** Focused, deterministic, good for math/code
- **Medium temperature (0.5-0.7):** Balanced, good for general use
- **High temperature (0.8-1.0):** Creative, diverse, good for writing

See [Configuration](../configuration/overview.md) for more details.

---

## Best Practices

### Ask Specific Questions

❌ "Python"  
✅ "How do I read a CSV file in Python?"

❌ "Math"  
✅ "What is the derivative of x^2 + 3x?"

### Let Routing Work Naturally

Don't try to force routing — the generalist will route appropriately:

❌ "Route this to the code specialist: write a function"  
✅ "Write a function to validate email addresses"

### Use Tools Implicitly

Don't explicitly request tool use — specialists invoke tools automatically:

❌ "Use the web_search tool to find information about AI"  
✅ "What is the latest news about AI?"

### Provide Context

More context = better results:

❌ "Fix this bug"  
✅ "Fix this Python bug: I'm getting 'list index out of range' on line 42"

---

## Next Steps

- **[Configuration Overview →](../configuration/overview.md)** — Understand the config file
- **[Specialists Configuration →](../configuration/specialists.md)** — Customize specialist behavior
- **[Built-in Tools Reference →](../tools/overview.md)** — See all available tools
- **[Routing Protocol →](../usage/routing.md)** — Deep dive into how routing works

---

## Getting Help

### Built-in Help

```bash
openjarvis --help
```

### Troubleshooting

See [Troubleshooting](../troubleshooting.md) for common issues and solutions.

### FAQ

See [FAQ](../faq.md) for frequently asked questions.

### GitHub Issues

Report bugs or request features: [github.com/bhanuponguru/OpenJarvis/issues](https://github.com/bhanuponguru/OpenJarvis/issues)
