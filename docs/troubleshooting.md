# Troubleshooting

Common issues and solutions for OpenJarvis.

---

## Installation Issues

### Binary Won't Execute (Linux)

**Error:** `Permission denied`

**Solution:**
```bash
chmod +x openjarvis
```

### Binary Won't Execute (macOS)

**Error:** "openjarvis cannot be opened because the developer cannot be verified"

**Solution:**
```bash
# Remove quarantine attribute
xattr -d com.apple.quarantine openjarvis
```

Or: System Preferences → Security & Privacy → Allow

### Binary Blocked (Windows)

**Error:** Windows Defender blocks the executable

**Solution:** Click "More info" → "Run anyway" in SmartScreen, or add an exception in Windows Security.

### Source Installation Fails

**Error:** `uv: command not found`

**Solution:** Install uv first:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Configuration Issues

### API Key Not Found

**Error:** `Error: Environment variable 'OPENAI_API_KEY' not set`

**Solution:**
```bash
export OPENAI_API_KEY="sk-..."
# Add to ~/.bashrc or ~/.zshrc for persistence
```

### Invalid Configuration File

**Error:** `Error: Could not load config file 'specialists.yaml'`

**Causes:**
1. File doesn't exist
2. Invalid YAML syntax
3. Missing required fields

**Solution:**
1. Check file exists: `ls specialists.yaml`
2. Validate YAML syntax with an online validator
3. Compare against [example configs](getting-started/quick-start.md)

### Model Not Found

**Error:** `Error: Model 'llama3' not found`

**For Ollama:**
```bash
# List available models
ollama list

# Pull missing model
ollama pull llama3
```

**For OpenAI:** Verify you're using a valid model name:
- `gpt-4o`
- `gpt-4o-mini`
- `gpt-4-turbo`

### Connection Refused

**Error:** `Error: Connection refused to http://localhost:11434`

**For Ollama:**
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama
ollama serve
```

**For other providers:** Verify the `base_url` in your config is correct.

---

## Runtime Issues

### No Routing Messages

**Problem:** OpenJarvis responds but doesn't show routing

**Cause:** Generalist is responding directly without routing

**Solution:** This is normal for simple queries. The generalist only routes when necessary.

### Routing Loops

**Problem:** Requests keep bouncing between specialists

**Example:**
```
routing: generalist → math → generalist → math → generalist
```

**Solution:** Check your system prompts. Specialists must know when to return:
```yaml
math:
  system_prompt: |
    Solve math problems.
    When done, end with [RETURN] to send back to generalist.
```

### Empty Responses

**Problem:** OpenJarvis returns nothing

**Causes:**
1. Model returned only routing tags (which are stripped)
2. API error
3. Model timeout

**Solution:**
1. Check logs with `--verbose`
2. Try a different model
3. Increase timeout (future feature)

### Tools Not Working

**Problem:** Specialists aren't using tools

**Solution:** Verify `delegates_to` includes `tool_use`:
```yaml
math:
  delegates_to: ["tool_use"]  # Required for tool access
```

### Code Execution Fails

**Error:** `Error executing Python code: [error message]`

**Causes:**
1. Syntax error in generated code
2. Missing Python modules
3. Permissions issue

**Solution:**
1. Ask specialist to fix the syntax
2. Install missing modules: `pip install [module]`
3. Check file/directory permissions

---

## Performance Issues

### Slow Responses

**Causes:**
1. Remote API latency
2. Large models on slow hardware (Ollama)
3. Multiple routing hops

**Solutions:**

**For remote APIs:**
- Use faster models (e.g., `gpt-4o-mini` instead of `gpt-4o`)
- Use Groq for fast inference

**For Ollama:**
- Use smaller models (`llama3` instead of `llama3:70b`)
- Upgrade hardware (more RAM/better GPU)

**For routing:**
- This is working as intended — complex queries need multiple hops

### High Memory Usage

**Cause:** Large models in Ollama

**Solution:**
- Use smaller models
- Close other applications
- Upgrade RAM

---

## API Issues

### Rate Limits

**Error:** `Error: Rate limit exceeded`

**Solution:**
- Wait before retrying
- Upgrade your API plan
- Use local models (Ollama)

### API Authentication Failed

**Error:** `Error: Authentication failed`

**Solution:**
1. Verify API key is correct
2. Check API key has sufficient permissions
3. Verify API key environment variable name matches config

### API Timeout

**Error:** `Error: Request timeout`

**Solution:**
- Check internet connection
- Try again later
- Use a faster provider

---

## Specialist-Specific Issues

### Math Specialist Returns Wrong Results

**Problem:** Calculations are incorrect

**Solutions:**
1. Lower temperature for precision:
   ```yaml
   math:
     temperature: 0.1  # More deterministic
   ```

2. Verify model has math capabilities (some models are better at math)

3. Use tool delegation:
   ```yaml
   math:
     delegates_to: ["tool_use"]  # Use calculator tool
   ```

### Code Specialist Generates Bad Code

**Solutions:**
1. Lower temperature:
   ```yaml
   code:
     temperature: 0.2
   ```

2. Use a code-specific model:
   ```yaml
   code:
     model: "codellama"  # For Ollama
     # or
     model: "gpt-4o"  # For OpenAI
   ```

3. Provide more context in your query

### Knowledge Specialist Provides Outdated Info

**Solution:** Verify `tool_use` delegation is enabled so specialist can search the web:
```yaml
knowledge:
  delegates_to: ["tool_use"]
```

---

## Debugging

### Enable Verbose Logging

```bash
openjarvis --verbose
```

This shows:
- API requests and responses
- Routing decisions
- Tool invocations
- Error details

### Check System Status

**Ollama:**
```bash
# Check if running
ps aux | grep ollama

# View logs
journalctl -u ollama -f  # Linux with systemd

# Test connection
curl http://localhost:11434/api/tags
```

**Python environment:**
```bash
# Check Python version
python --version  # Should be 3.13+

# Check OpenJarvis installation
openjarvis --version
```

### Test Configuration

```bash
# Validate config file exists
cat specialists.yaml

# Test with simple query
echo "What is 2 + 2?" | openjarvis
```

---

## Getting More Help

### Documentation

- [Configuration Guide](configuration/overview.md)
- [Built-in Tools](tools/overview.md)
- [FAQ](faq.md)

### GitHub Issues

Search existing issues or create a new one:
[github.com/bhanuponguru/OpenJarvis/issues](https://github.com/bhanuponguru/OpenJarvis/issues)

**When reporting issues, include:**
1. OpenJarvis version (`openjarvis --version`)
2. Operating system
3. Configuration file (remove API keys!)
4. Error message
5. Steps to reproduce

### Community

- GitHub Discussions (coming soon)
- Discord server (coming soon)

---

## Common Error Messages

### "Could not find specialist X"

**Cause:** Generalist or specialist tried to route/delegate to a specialist that doesn't exist in config

**Solution:** Add the specialist to your config, or fix the routing logic

### "Circular delegation detected"

**Cause:** Specialist A delegates to B, B delegates to A

**Solution:** Remove circular delegation from `delegates_to`

### "Maximum routing depth exceeded"

**Cause:** Too many routing hops (safety limit)

**Solution:** Simplify your delegation graph or check for loops

### "Tool execution not allowed"

**Cause:** Specialist tried to use tools but doesn't delegate to `tool_use`

**Solution:** Add `tool_use` to `delegates_to`:
```yaml
math:
  delegates_to: ["tool_use"]
```

---

## Still Having Issues?

If you're still stuck:

1. Check [FAQ](faq.md) for common questions
2. Search [GitHub Issues](https://github.com/bhanuponguru/OpenJarvis/issues)
3. Create a new issue with details
4. Join the community (links coming soon)
