# User Access

To control who has access to an Organization, and what they have access to, go to the "Users" section of the web application.

Adding users is done by email address and requires the user to already have a limacharlie.io account.

The first user of an organization is added with Owner permissions at creation time. Owner permissions give full access to everything.

New users added after the creation of an organization are added with Unset privileges, which means the user is only able to get the most basic information on the organization.

Therefore, the first step after adding a new user should always be to change their permissions by clicking the Edit icon beside their name.

Permissions can be controlled individually, or you can apply pre-set permission schemes by selecting it at the top of the dialog box, clicking Apply, and then clicking the Save button at the bottom.

User Permissions

We offer granular user permissions, allowing you to customize what roles and how much access users should have. For a full list of permissions, see [Reference: Permissions](/v2/docs/reference-permissions).

## Access on a per-organization basis

To add a user to an Organization, the new user needs to first create their own LimaCharlie account.

After the new user has created their LimaCharlie account, you can add them by inputting their email account to your Organization.

After adding the user, you have the ability to control what permissions they get in this tenant. To do so, click on their email and adjust their permissions in the modal that opens. (See information about user permissions above).

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/NewSS_1.png)

## Access via Organization Groups

Groups allow you to grant permissions to a set of users on a group of organizations. To get started, navigate to the upper right section of the web app and select groups.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/NewSS_2.png)

From there, create a new group or click to edit an existing one.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/NewSS_3.png)

The user who creates a group becomes a group owner. Group owners manage the group but do not have permissions themselves.

You can add multiple group owners.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/NewSS4.png)

In the **Users** section (left panel), you can add all existing users who should receive access to the organizations included in this group. Note that if you are a Group Owner and you want the permissions of this group to apply to yourself, you will need to add your email here as well.

Adding Accounts

Note that all accounts will need to be _existing_ LimaCharlie users.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/NewSS_5.png)

Group owners are allowed to manage the group, but are not affected by the permissions. Members are affected by the permissions but cannot modify the group.

Under **Organizations**(left panel), select a list of organizations you have access to. Note that in order to add an organization to the group, you need to have the user.ctrl permission enabled for that organization.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/NewSS_6.png)

Last, select the permissions you want members of the group to have in the organizations included in this group.

Permissions granted through the group are applied on top of permissions granted at the organization level. The permissions are additive, and a group cannot be used to subtract permissions granted at the organization level.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/NewSS_7.png)

To finish, click `Update Permissions` at the top right corner.

To review activity that has occurred in this group, click on **Activity Logs** (left panel).

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image\(343\).png)

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.
