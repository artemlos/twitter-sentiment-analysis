The program run from monday to tuesday terminated due to OutOfMemory exception. All the results that were recorded have a 'monday' suffix.

```
Exception in thread "JobGenerator" java.lang.OutOfMemoryError: Java heap space
	at java.util.Arrays.copyOfRange(Arrays.java:3664)
	at java.lang.StringBuffer.toString(StringBuffer.java:669)
	at java.io.BufferedReader.readLine(BufferedReader.java:359)
	at java.io.BufferedReader.readLine(BufferedReader.java:389)
	at py4j.CallbackConnection.readBlockingResponse(CallbackConnection.java:169)
```
