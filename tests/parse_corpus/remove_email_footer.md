CI/CD configuration files do more than automate builds. They decide which checks gate a merge, how failures are bounded, when artifacts are published, and what paths lead to deployment. In other words, they encode operational policy. For software-intensive systems, that policy has direct consequences for reliability, security, release cadence, and infrastructure cost. Recent work has shown that LLMs can recover common CI/CD stages directly from raw workflow files at scale [1]. Useful as that result is, it still leaves the main engineering questions open: Which workflows look fragile? What counts as normal for a given ecosystem? Which fixes are worth a maintainer’s time? 

We study those questions by treating CI/CD workflows as analyzable infrastructure rather than passive configuration text. Our pipeline begins with a large GitHub corpus, enriches repositories with language and domain metadata, scans workflows for anti-patterns and stage structure, and then generates repository-level recommendations with sev- 

> 1Independent Researcher shenbonan2@gmail.com 

> 2Independent Researcher gjz140103@gmail.com 

> 3Independent Researcher ntgd1102@gmail.com 

> 4Independent Researcher william.wj.huang@gmail.com 

> 5Independent Researcher iamxinliu@gmail.com 



<!-- Start of picture text -->
Issue distributions<br>top categories<br>domain joins<br>LLM analysis pipeline<br>GitHub Corpus Metadata Enrichment RQ1 Detector<br>59,550 repos topics + domain labels 75,201 configs<br>127,559 configs 32,513 repos anti-pattern JSON<br>RQ3 Generator RQ2 Detector<br>34k repos/strategy 59,906 configs<br>YAML repairs stages + triggers<br>Prompting comparison Language significance<br>validity analysis domain stage profiles<br><!-- End of picture text -->

Fig. 1. Study overview. The artifact extends CI/CD analysis from coarse stage recognition to a connected pipeline that enriches repositories, mines anti-patterns and stages, and generates actionable repair suggestions. 

eral prompting strategies. The goal is not to replace maintainers with an autonomous fixer. The goal is to give them a clearer picture of operational risk and a better starting point for intervention. 