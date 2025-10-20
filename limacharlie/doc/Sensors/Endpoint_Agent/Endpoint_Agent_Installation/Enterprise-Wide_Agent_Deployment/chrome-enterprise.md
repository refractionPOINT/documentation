# ChromeOS with Google Chrome Enterprise

You can mass deploy the LimaCharlie Sensor for ChromeOS with Google Workspace and [Google Chrome Enterprise](https://chromeenterprise.google/).

## Configuration

1. Log into Google Workspace Admin and go to [Devices -> Chrome -> Apps & extensions -> Users & Browsers](https://admin.google.com/ac/chrome/apps/user).
2. In the **Users & browsers** tab click the "+" button in the bottom right, then choose the option to "Add from Chrome Web Store".
3. Search for the [LimaCharlie Sensor](https://chrome.google.com/webstore/detail/limacharlie-sensor/ljdgkaegafdgakkjekimaehhneieecki) extension and click Select.
4. Click on the LimaCharlie Sensor app to show the installation policy.
5. Set the "Installation Policy" to "Force install".
6. Set the "Policy for extensions" value as follows:

```
{
    "installation_key": {
        "Value": "\"KEY\""
    }
}
```

IMPORTANT: Replace the text "KEY" with the actual value of your Installation Key, in particular the **Chrome Key** which you can obtain from within the LimaCharlie web app.

*Example*
![App_Management_-_Admin_Console.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/App_Management_-_Admin_Console.png)

## Verifying Configuration

ChromeOS endpoints should now start appearing within the related LimaCharlie Organization's sensor list.

You can verify that the configuration was completed successfully by verifying on an individual endpoint.

1. Confirm that the LimaCharlie Sensor extension appears in the list of extensions.
2. Verify that the installation key got applied on the endpoint by going to:  `chrome://policy` and look for the LimaCharlie Sensor. There you should see the Policy name set to `installation_key` and the Policy Value set with your installation key. The Source should list "Cloud".

![endpoint.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/endpoint.png)
