# Chrome Agent Installation

The LimaCharlie Chrome sensor is a browser extension. It gives visibility of the activity inside the browser. The sensor is useful to get network visibility at low cost in organizations that use ChromeOS a lot.

LimaCharlie supplies it as the [LimaCharlie Sensor](https://chrome.google.com/webstore/detail/limacharlie-sensor/ljdgkaegafdgakkjekimaehhneieecki) extension in the Chrome Web Store.

## Installation Instructions

The Chrome sensor is available in the Chrome Web Store.

1. In the LimaCharlie web app (app.limacharlie.io), go to the "Installation Keys" section.
2. Select your installation key.
3. Click the "Chrome Key" copy icon. The web app copies the key to your clipboard.
4. Install the sensor from: <https://downloads.limacharlie.io/sensor/chrome>
5. In the new tab that opens, enter the installation key from step 3. If you close the tab by mistake, open the options again:

    1. On the Extensions page at chrome://extensions/, click the "Details" button of the LimaCharlie Sensor extension.
    2. Go to the "Extension options" section.
    3. Enter the installation key from the previous step. Click save.

If you use a managed Chrome deployment, you can set the installation key in advance with the Managed Storage feature. The key name is `installation_key`.

## Troubleshooting the Chrome Sensor

If the Chrome extension has connectivity problems, these steps can help.

First, uninstall the extension and install it again.

If the extension still does not connect, send these details to the LimaCharlie support team:

1. Open a new browser tab.
2. Go to `chrome://extensions/`.
3. Make sure that "Developer Mode" is on. The toggle is in the top right.

    ![image.png](../../../assets/images/image(38).png)

4. Click the `background.html` link in the LimaCharlie Sensor entry.

    ![image.png](../../../assets/images/image(39).png)

5. In the window that opens, click Console. Send a screenshot of the console output for analysis.

Also include your Organization ID. You find it in the LimaCharlie web app in the REST API section under `OID`.
