New post on terraphim.ai: a checklist is an enumerated set of terms, so it belongs in the Aho-Corasick automaton rather than a vector index or a system-prompt promise.

Before the LLM call, terraphim-grep with a role thesaurus expanded 'quality gate' into eight concepts and matched chunks in files containing none of the query words; the 'checklist' control honestly reported kg_hits: 0. After the call, terraphim-agent hook returns a machine-readable findings list, and learn/memory feeds corrections back into the synonym set.

The post quotes real outputs only, including one caveat: in this build terraphim-agent replace reports changed:true without substituting, so the findings-based hook is the contract. The public 39-entry graph subset is committed in the site repo.

https://terraphim.ai/posts/graph-embeddings-checklists/

Which checklist in your agent setup would you enforce with an automaton rather than a prompt?
