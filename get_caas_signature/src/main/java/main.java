import java.io.UnsupportedEncodingException;
import java.net.URLDecoder;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.time.Instant;
import org.apache.commons.codec.binary.Base64;
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.LambdaLogger;

public class main {

    public String handler(String input, Context context) {
        LambdaLogger logger = context.getLogger();
        String utcTime = Instant.now().plus(
                15,ChronoUnit.SECONDS).truncatedTo(ChronoUnit.SECONDS).toString();
        logger.log("Expire time: " + utcTime + "\n");
        String secretKey = System.getenv("secretKey");
        String accessKey = System.getenv("accessKey");
        String signedUrl = getSignedUrl(secretKey,
                input + "&accessKey=" + accessKey + "&expires=" + utcTime);
        logger.log(signedUrl);
        return signedUrl;
    }

    // Below is from https://hws.hicloud.hinet.net/hws-doc/zh_TW/rest/tutorial/howto-gen-signature.html

    public static String getSignedUrl(String userSecretKey, String unsignedUrl){
        String commandString  =unsignedUrl.substring(unsignedUrl.indexOf('?') + 1);
        return unsignedUrl + "&signature=" + generateSignature(userSecretKey, commandString);
    }

    public static  String generateSignature(String userSecretKey, String commandString) {
        Map<String, List<String>> arguments = new HashMap<String, List<String>>();
        String decodedUrl = "";
        try {
            decodedUrl = URLDecoder.decode(commandString, "utf8");
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        }

        String [] commands = decodedUrl.split("&");
        for(String command : commands) {
            String [] keyValues = command.split("=");
            if(arguments.containsKey(keyValues[0])){
                List<String> valueList=arguments.get(keyValues[0]);
                valueList.add(keyValues[1]);
            } else{
                List<String> valueList = new ArrayList<String>();
                valueList.add(keyValues[1]);
                arguments.put(keyValues[0], valueList);
            }
        }
        return generateSignature(userSecretKey, arguments);
    }

    public static String generateSignature(String userSecretKey, Map<String, List<String>> arguments){

        List<String> argumentNameList = new ArrayList<String>();
        String mySignature = null;

        for(String name : arguments.keySet()) {
            argumentNameList.add(name);
        }
        Collections.sort(argumentNameList);

        String requestMsg = null;
        for(String argumentName : argumentNameList){
            List<String> valueList = arguments.get(argumentName);
            for(int listCount=0 ; listCount<valueList.size() ; listCount++){
                if(requestMsg == null){
                    requestMsg = argumentName + "=" + valueList.get(listCount);
                }else {
                    requestMsg += "&" + argumentName + "=" + valueList.get(listCount);
                }
            }
        }
        requestMsg = requestMsg.toLowerCase();
        //System.out.println(requestMsg);
        try {
            Mac mac;
            mac = Mac.getInstance("HmacSHA1");
            SecretKeySpec keySpec = new SecretKeySpec(userSecretKey.getBytes(), "HmacSHA1");
            mac.init(keySpec);
            mac.update(requestMsg.getBytes());
            byte[] encryptedBytes = mac.doFinal();
            mySignature = getBase64String(encryptedBytes);
        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
        } catch (InvalidKeyException e) {
            e.printStackTrace();
        }
        return mySignature;
    }

    private static String getBase64String(byte[] encryptedBytes) {
        String encodeString = null;
        encodeString = new String(Base64.encodeBase64(encryptedBytes));
        encodeString = encodeString.replace("+", "*");
        encodeString = encodeString.replace("/", "-");
        encodeString = encodeString.replace("=", "");
        return encodeString;
    }
}