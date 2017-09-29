import twitter
import json

api = twitter.Api(consumer_key='pnQFCZpsEfUxdmCOXiOYgEQDA',
                  consumer_secret='lbnlPekP1lNIODvC4U8lwOnlO8r2MFPAr8VpnL2JYM4TL94MGE',
                  access_token_key='218891284-vDatV2MOCc8j0MdVmHnZM40tZmfaymgUOZEKnYhC',
                  access_token_secret='lWeGDsq9FUL8uGaYb4JkQ2kXllH2mx3jbtG4sdPS3059L')

# print(api.VerifyCredentials())

results = api.GetSearch(
    term="amazon",
    count=10,
    result_type="recent",
    lang="en")

print(results[1])
