### How the authentication works with ASANA
Register the application and get the **client ID** and **client secret**. These are saved as environment variables
Credential will arrive at the application and click a button that says "Connect with Asana"  
This takes the customer to the Credential Authorization Endpoint  
If the customer clicks "Allow", they are redirected back to the application,
bringing along a special code as a query parameter (Authorization Code Grant)   
The application can now use the Token Exchange Endpoint to exchange the code, together with the Client Secret,
for a Bearer Token (which lasts an hour), and a Refresh Token (which can be used to fetch new Bearer
Tokens when the current one expires)  
Once the Bearer Token expires, the application can again use the Token Exchange Endpoint to
exchange the Refresh Token for a new Bearer Token  

### State generation
We are sending a random state to the Credential Authorization Endpoint to improve security. 
Resource: https://auth0.com/docs/protocols/state-parameters  

Note: I will be actually using Asana's official Python package. https://github.com/Asana/python-asana/  