Graph embeddings for checklists

A checklist is an enumerated set of terms that must be checked. Vector embeddings return fuzzy neighbours; they cannot enumerate a fixed set and report which members fired. A knowledge graph can.

I wrote up the machinery that wraps a Terraphim checklist around an LLM call. Before the call, terraphim-grep expands a query through a role thesaurus: 'quality gate' matched eight concepts in 53 ms, in files containing none of the query words. A control query reports kg_hits: 0 and says so. After the call, terraphim-agent hook returns a machine-readable findings list instead of a silent rewrite, and learn/memory feeds corrections back into the synonym set.

Every command output in the post is real, and the 39-entry public subset of the graph is committed in the site repo so you can run the same commands.

Which checklist in your agent setup would you rather see enforced by an automaton than by a system-prompt promise?

https://terraphim.ai/posts/graph-embeddings-checklists/
