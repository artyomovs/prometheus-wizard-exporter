# prometheus-wizard-exporter
## Customized python Prometheus exporter (docker container)


> Prometheus+grafana are a couple of guys, that could help with everything (except for the weather, money issues, college, etc. ). Ok, they could help with everything in the world of monitoring.

Fortunately, there are a bunch of handful prometheus-exporters, that could expose metrics of different systems (Linux, Windows, web servers, elasticsearch, etc.).

One day I got a couple of almost similar tasks - 1. get website Sign In time. 2. get elasticsearch [CCR](https://www.elastic.co/guide/en/elasticsearch/reference/current/ccr-get-stats.html) request response time.
Of course, I could solve these tasks with a [blackbox-exporter](https://github.com/prometheus/blackbox_exporter), but there are some nuances here. For example
1. The HTTP request could be [with more than one step](https://www.elastic.co/guide/en/elasticsearch/reference/current/tasks.html). i.e. POST exmaple.com/task (get task_id) GET example.com/task_id (get result)
2. I needed a frontend check of my website, so I needed something like [selenium](https://github.com/SeleniumHQ/selenium) or [puppeteer](https://github.com/puppeteer/puppeteer)

I decided to create my own <b>prometheus-wizard-exporter</b>. A python core (run as docker container) that executes scripts with schedule from the "libs" directory and just expose these scripts metrics. Now, if I want to add metrics to measure - I follow this scenario:

1. Create a python script in the libs directory.
2. Add the name of script and function to YAML input
3. Rebuild docker image.
