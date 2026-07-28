# Test a New Sensor Version

Test a new Sensor version before you roll it out. The test makes sure that the Sensor works correctly in your environment. LimaCharlie tests Sensors before it releases them, but it cannot predict each niche use case. Test on `dev` or `test` systems before you deploy in production. This removes concerns about resource use and about Sensor operations.

You test a sensor version with the tagging functionality of LimaCharlie.

When you tag a Sensor with `lc:latest`, that sensor ignores the sensor version that is assigned to the Organization. It uses the latest version of the sensor instead. Apply this tag to a small number of systems to test-deploy the latest version.

You can also tag a sensor with `lc:stable`. That sensor then ignores the sensor version that is assigned to the Organization, and uses the stable version of the sensor instead.

To tag a Sensor, open the sensors list. Select the sensor that you want to test. Go to the `tags` field on the sensor `Overview`.

![Alternatively, you can tag a sensor with lc:stable](../../assets/images/image(314).png)

Type `lc:stable` and click `Update Tags`.

Note: It can take up to 10 minutes to update the sensor to the tagged version.
