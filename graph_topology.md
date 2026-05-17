`mermaid
---
config:
  flowchart:
    curve: linear
---
graph TD;
	__start__([<p>__start__</p>]):::first
	router(router)
	retrieve_from_store(retrieve_from_store)
	search_web(search_web)
	fetch_weather(fetch_weather)
	fetch_images(fetch_images)
	synthesizer(synthesizer)
	__end__([<p>__end__</p>]):::last
	__start__ --> router;
	fetch_images --> synthesizer;
	fetch_weather --> synthesizer;
	retrieve_from_store --> fetch_images;
	retrieve_from_store --> fetch_weather;
	router -. &nbsp;fetch_data&nbsp; .-> fetch_weather;
	router -.-> retrieve_from_store;
	router -.-> search_web;
	search_web --> fetch_images;
	search_web --> fetch_weather;
	synthesizer --> __end__;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc

`
