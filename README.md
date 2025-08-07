Prompting Strategy

Prompting strategy guides the LLM to extract and classify information from raw HTML by providing a structured prompt.
The key elements are-
Specific instructions: The prompt explicitly tells the LLM to "Extract distinct recycling facilities from the raw HTML" and to return the data as a valid JSON array.
Output format definition: I defined a precise JSON schema, specifying the exact keys (business_name, last_update_date, etc.) and the expected data types for each field.
Categorization guidance: To classify materials, it instructs the LLM to infer the correct category for each facility based on the "materials accepted" list found in the HTML. This step ensures classification.
Handling missing data: The prompt gets missing information, specifically for the last_update_date, by instructing the LLM to use "Unknown" if the date isn't available.

Pipeline Structure

The solution uses a LangChain chain to connect a prompt template with a language model.
Prompt Template: A PromptTemplate is used to define the instructions and the JSON format. It has a placeholder, {scraped_html}, where the raw HTML data is inserted. This template acts as a blueprint for the LLM's task.
LLM: The ChatGoogleGenerativeAI model, specifically gemini-1.5-flash, is used in this program. It receives the complete prompt (template + HTML) and performs the extraction and classification.
Chain: The RunnableSequence chain = prompt_template | llm combines these two components. This structure is simple and effective. It takes the HTML, formats it according to the prompt_template, and then passes the result to the llm for processing.

Handling Edge Cases

Nested HTML: The prompt instructs the LLM to focus on `<li class="result-item">` tags, which represent individual facilities. By sending only the relevant HTML snippets to the LLM , it avoids getting confused by the deeply nested elements.
Map-only data: The current solution relies on the text-based search results. If a page only contains map data without corresponding HTML list items, the BeautifulSoup selector soup.select('ul.result-list > li.result-item') will return an empty list. In this case, the LLM will receive no HTML and will not be able to extract any facilities. 
Inconsistent labeling: The prompting strategy is designed to handle this by making the LLM to get the materials_category from the materials_accepted list. Meaning, even if a facility's HTML doesn't explicitly state "Electronics," the LLM can get the category if the accepted materials include "Computers" and "Smartphones," for example.
