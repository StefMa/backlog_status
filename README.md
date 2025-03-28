# Backlog status ✨

Get the status of your "backlog" ticket from OpenAI in natural language.

## Example
**Question/Prompt:**
> Status of ticket dynamic rating

**Answer:**

<details open=true>
<summary>OpenAI final response</summary>

### Ticket Status Summary

**Issue Title:** [Dynamic Rating Options](https://github.com/StefMa/backlog_status/issues/1)
**Overall Progress:** 33% completed (1 out of 3 sub-issues completed)

#### Sub-Issues Details:

1. **[Dynamic Rating Options - Android](https://github.com/StefMa/backlog_status/issues/2)**
   - **Assignees:** None
   - **Status:** Open

2. **[Dynamic Rating Options - iOS](https://github.com/StefMa/backlog_status/issues/3)**
   - **Assignees:** StefMa
   - **Status:** Open

3. **[Dynamic Rating Options - Backend](https://github.com/StefMa/backlog_status/issues/4)**
   - **Assignees:** StefMa
   - **Status:** Closed

### Summary of Assignees:
- **StefMa** is currently assigned to the iOS and Backend sub-issues.

For further details, you can follow the links to each sub-issue. Let me know if you need any more information!

</details>

## How?

### Setup

* Clone this repo
* Create a virtual environment:
```
python -m venv venv
```
* Install required dependencies
```
./venv/bin/pip install -r requirements.txt
```

Further you need
* OpenAI API Token
* A "backlog" ticket that contains sub-issues
* (Optional) GitHub Token / Only for private repositories

### Run

```
./venv/bin/python backlog_status.py \
  --openai-token TOKEN \
  --repo Owner/Repo  \
  --github-token TOKEN \
  "Your prompt. E.g: Status of ticket 2266"
```

## Why?

This was just an experiment how to use OpenAI [function calling](https://platform.openai.com/docs/guides/function-calling) feature.
