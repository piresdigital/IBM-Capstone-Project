const { CloudantV1 } = require('@ibm-cloud/cloudant');
const { IamAuthenticator } = require('ibm-cloud-sdk-core');

async function main(params) {
  const authenticator = new IamAuthenticator({ apikey: params.IAM_API_KEY });
  const cloudant = CloudantV1.newInstance({
    authenticator: authenticator,
  });
  cloudant.setServiceUrl(params.COUCH_URL);

  const database = 'dealerships';

  if (params.state) {
    try {
      const query = await cloudant.postFind({
        db: database,
        selector: { st: params.state },
      });

      return query.result;
    } catch (err) {
      if (err.status == 404) {
        return { error: 'The state does not exist' };
      } else {
        return { error: err.description };
      }
    }
  } else if (params.dealerId) {
    try {
      const query = await cloudant.postFind({
        db: database,
        selector: { id: parseInt(params.dealerId) },
      });

      return query.result;
    } catch (err) {
      if (err.status == 404) {
        return { error: 'The state does not exist' };
      } else {
        return { error: err.description };
      }
    }
  } else {
    try {
      const query = await cloudant.postAllDocs({
        db: database,
        includeDocs: true,
      });
      return query.result;
    } catch (err) {
      if (err.status == 404) {
        return { error: 'Database is empty' };
      } else {
        return { error: 'Something went wrong on the server' };
      }
    }
  }
}
