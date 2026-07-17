## **4. Proposed Method** 

Our proposed approach is Method 1, in which raw audio is forwarded directly to a multimodal LLM for scam detection without any preprocessing. Methods 2 and 3 serve as comparison baselines using text-based input. In Method 2, audio is first converted to text via the Scribe V1 ASR system and passed to the LLM without correction. In Method 3, the 

|**Method 1**|**Method 2**<br>**Method 3**|
|---|---|
|Audio fle<br>LLM<br>Prediction|Audio fle<br>ASR (Scribe V1)<br>Transcript<br>Audio fle<br>ASR (Scribe V1)<br>Transcript|
|(Raw Audio)|LLM<br>Prediction<br>(Unchecked<br>Transcript)<br>Native speaker review<br>LLM<br>Prediction<br>(Checked Transcript)|



Figure 1. Three input conditions evaluated in this study. 

ASR transcript is further reviewed and corrected by a fluent Turkish speaker before being passed to the LLM.