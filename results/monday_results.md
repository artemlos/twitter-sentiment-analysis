The program run from monday to tuesday terminated due to OutOfMemory exception. All the results that were recorded have a 'monday' suffix.

```
Exception in thread "JobGenerator" java.lang.OutOfMemoryError: Java heap space
	at java.util.Arrays.copyOfRange(Arrays.java:3664)
	at java.lang.StringBuffer.toString(StringBuffer.java:669)
	at java.io.BufferedReader.readLine(BufferedReader.java:359)
	at java.io.BufferedReader.readLine(BufferedReader.java:389)
	at py4j.CallbackConnection.readBlockingResponse(CallbackConnection.java:169)
```

Note that experiments were restarted several times due to crashes in actual_val.txt, decay_window.txt and smooth_fast.txt. This can be clearly observed in decay_window since it starts with small values that increase rapidly. actual_val.txt is the unprocessed data which just tells the sentiment score at that time.