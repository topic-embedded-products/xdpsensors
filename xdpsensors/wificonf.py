from twisted.web import resource

import subprocess

def wpa(args):
    cmd = ["wpa_cli", "-i", "wlan0"] + args
    return subprocess.check_output(cmd)

class WifiResource(resource.Resource):
    def render_GET(self, request):
        request.responseHeaders.addRawHeader(b"content-type", b"text/html")
        statustext = subprocess.check_output(["wpa_cli", "-i", "wlan0", "status"])
        scan = subprocess.check_output(["wpa_cli", "-i", "wlan0", "scan_results"])
        return """<html>
<head><title>Wifi Configuration</title></head>
<body>
<h1>WiFi authenticate</h1>
<form method="POST">
  <label for="ssid">SSID:</label><br>
  <input type="text" id="ssid" name="ssid"><br>
  <label for="passphrase">Passphrase:</label><br>
  <input type="text" id="passphrase" name="passphrase"><br>
  <br>
  <input type="submit" value="Connect">
</form> 
<h1>WiFi status</h1>
<pre>%s</pre>
<h1>WiFi scan results</h1>
<pre>%s</pre>
</body>
</html>
""" % (statustext, scan)
    def render_POST(self, request):
        request.responseHeaders.addRawHeader(b'refresh', b'5; url=/wifi')
        ssid = request.args['ssid'][0]
        passphrase = request.args['passphrase'][0]
        if (len(ssid) < 3) or (len(passphrase) < 8):
            r = "Not a valid SSID and passphrase"
        else:
            n = wpa(["add_network"]) # Returns number
            r = wpa(["set_network", n, "ssid", '"%s"' % ssid]) # must be quoted
            r = wpa(["set_network", n, "psk", '"%s"' % passphrase])
            r = wpa(["enable_network", n])
        return """<html>
<head><title>Wifi Configuration</title></head>
<body>
<h1>WiFi authenticate result</h1>
<pre>%s</pre>
</body>
</html>
""" % (r)
