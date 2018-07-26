import  java.util.Base64;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.io.IOException;
import java.io.InputStream;
import java.io.UnsupportedEncodingException;
import java.net.URL;
import java.net.URLConnection;
import java.net.HttpURLConnection;
import java.net.URLEncoder;
import java.security.SignatureException;
import java.security.MessageDigest;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.*;

/**
 * Makes a request to the Alexa Web Information Service UrlInfo action.
 */
public class UrlInfo {

    private static final String ACTION_NAME = "UrlInfo";
    private static final String RESPONSE_GROUP_NAME = "Rank,LinksInCount";
    private static final String SERVICE_HOST = "awis.amazonaws.com";
    protected static final String SERVICE_ENDPOINT = "awis.us-west-1.amazonaws.com";
    private static final String SERVICE_URI = "/api";
    private static final String SERVICE_REGION = "us-west-1";
    private static final String SERVICE_NAME = "awis";
    private static final String AWS_BASE_URL = "https://" + SERVICE_HOST + SERVICE_URI;
    private static final String HASH_ALGORITHM = "HmacSHA256";
    private static final String DATEFORMAT_AWS = "yyyyMMdd'T'HHmmss'Z'";
    private static final String DATEFORMAT_CREDENTIAL = "yyyyMMdd";

    private String accessKeyId;
    private String secretAccessKey;
    private String site;

    public String amzDate;
    public String dateStamp;

    public UrlInfo(String accessKeyId, String secretAccessKey, String site) {
        this.accessKeyId = accessKeyId;
        this.secretAccessKey = secretAccessKey;
        this.site = site;

        Date now = new Date();
        SimpleDateFormat formatAWS = new SimpleDateFormat(DATEFORMAT_AWS);
        formatAWS.setTimeZone(TimeZone.getTimeZone("GMT"));
    		this.amzDate = formatAWS.format(now);

        SimpleDateFormat formatCredential = new SimpleDateFormat(DATEFORMAT_CREDENTIAL);
        formatCredential.setTimeZone(TimeZone.getTimeZone("GMT"));
        this.dateStamp = formatCredential.format(now);
    }

    String sha256(String textToHash) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] byteOfTextToHash=textToHash.getBytes("UTF-8");
        byte[] hashedByteArray = digest.digest(byteOfTextToHash);
        return bytesToHex(hashedByteArray);
    }

    static byte[] HmacSHA256(String data, byte[] key) throws Exception {
        Mac mac = Mac.getInstance(HASH_ALGORITHM);
        mac.init(new SecretKeySpec(key, HASH_ALGORITHM));
        return mac.doFinal(data.getBytes("UTF8"));
    }

    public static String bytesToHex(byte[] bytes) {
        StringBuffer result = new StringBuffer();
        for (byte byt : bytes) result.append(Integer.toString((byt & 0xff) + 0x100, 16).substring(1));
        return result.toString();
    }

    /**
     * Generates a V4 Signature key for the service/region
     *
     * @param key         Initial secret key
     * @param dateStamp   Date in YYYYMMDD format
     * @param regionName  AWS region for the signature
     * @param serviceName AWS service name
     * @return byte[] signature
     * @throws Exception
     */
    static byte[] getSignatureKey(String key, String dateStamp, String regionName, String serviceName) throws Exception {
        byte[] kSecret = ("AWS4" + key).getBytes("UTF8");
        byte[] kDate = HmacSHA256(dateStamp, kSecret);
        byte[] kRegion = HmacSHA256(regionName, kDate);
        byte[] kService = HmacSHA256(serviceName, kRegion);
        byte[] kSigning = HmacSHA256("aws4_request", kService);
        return kSigning;
    }

    /**
     * Makes a request to the specified Url and return the results as a String
     *
     * @param requestUrl url to make request to
     * @return the XML document as a String
     * @throws IOException
     */
    public static String makeRequest(String requestUrl, String authorization, String amzDate) throws IOException {
        URL url = new URL(requestUrl);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestProperty("Accept", "application/xml");
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setRequestProperty("X-Amz-Date", amzDate);
        conn.setRequestProperty("Authorization", authorization);

        InputStream in = (conn.getResponseCode() / 100 == 2 ? conn.getInputStream() : conn.getErrorStream());

        // Read the response
        StringBuffer sb = new StringBuffer();
        int c;
        int lastChar = 0;
        while ((c = in.read()) != -1) {
            if (c == '<' && (lastChar == '>'))
                sb.append('\n');
            sb.append((char) c);
            lastChar = c;
        }
        in.close();
        return sb.toString();
    }

    /**
     * Makes a request to the Alexa Web Information Service UrlInfo action
     */
    public static void main(String[] args) throws Exception {

        if (args.length < 3) {
            System.err.println("Usage: UrlInfo ACCESS_KEY_ID " +
                               "SECRET_ACCESS_KEY site");
            System.exit(-1);
        }

        // Read command line parameters

        String accessKey = args[0];
        String secretKey = args[1];
        String site = args[2];

        UrlInfo urlInfo = new UrlInfo(accessKey, secretKey, site);
		int counter = 1;

        //String canonicalQuery = "Action=" + "urlInfo" + "&ResponseGroup=" + URLEncoder.encode(RESPONSE_GROUP_NAME, "UTF-8") + "&Url=" + URLEncoder.encode(site, "UTF-8");
		String canonicalQuery = "Action=CategoryListings&Count=20&Descriptions=True&Path=Top%2FNews&Recursive=False&ResponseGroup=Listings&SortBy=Popularity&Start=" + counter;
        String canonicalHeaders = "host:" + SERVICE_ENDPOINT + "\n" + "x-amz-date:" + urlInfo.amzDate + "\n";
        String signedHeaders = "host;x-amz-date";

        String payloadHash = urlInfo.sha256("");

        String canonicalRequest = "GET" + "\n" + SERVICE_URI + "\n" + canonicalQuery + "\n" + canonicalHeaders + "\n" + signedHeaders + "\n" + payloadHash;

        // ************* TASK 2: CREATE THE STRING TO SIGN*************
        // Match the algorithm to the hashing algorithm you use, either SHA-1 or
        // SHA-256 (recommended)
        String algorithm = "AWS4-HMAC-SHA256";
        String credentialScope = urlInfo.dateStamp + "/" + SERVICE_REGION + "/" + SERVICE_NAME + "/" + "aws4_request";
        String stringToSign = algorithm + '\n' +  urlInfo.amzDate + '\n' +  credentialScope + '\n' +  urlInfo.sha256(canonicalRequest);

        // ************* TASK 3: CALCULATE THE SIGNATURE *************
        // Create the signing key
        byte[] signingKey = urlInfo.getSignatureKey(secretKey, urlInfo.dateStamp, SERVICE_REGION, SERVICE_NAME);

        // Sign the string_to_sign using the signing_key
        String signature = bytesToHex(HmacSHA256(stringToSign, signingKey));

        String uri = AWS_BASE_URL + "?" + canonicalQuery;

        System.out.println("Making request to:\n");
        System.out.println(uri + "\n");

        // Make the Request

        String authorization = algorithm + " " + "Credential=" + accessKey + "/" + credentialScope + ", " +  "SignedHeaders=" + signedHeaders + ", " + "Signature=" + signature;

        String xmlResponse = makeRequest(uri, authorization, urlInfo.amzDate);

        // Print out the XML Response

        System.out.println("Response:\n");
        System.out.println(xmlResponse);
    }
}
