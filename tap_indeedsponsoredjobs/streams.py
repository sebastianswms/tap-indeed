"""Stream type classes for tap-indeedsponsoredjobs."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable
from singer_sdk import typing as th  # JSON Schema typing helpers
from memoization import cached
from singer_sdk.authenticators import OAuthAuthenticator
from tap_indeedsponsoredjobs.client import IndeedSponsoredJobsStream
from tap_indeedsponsoredjobs.auth import IndeedSponsoredJobsAuthenticator

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class Employers(IndeedSponsoredJobsStream):
    """List of all employers we have access to"""
    name = "employers"
    path = "/appinfo"
    primary_keys = ["id"]
    replication_key = None
    records_jsonpath = "$.['employers'][*]"  # Or override `parse_response`.
    url_base = "https://secure.indeed.com/v2/api"

    @property
    @cached
    def authenticator(self) -> IndeedSponsoredJobsAuthenticator:
        """Return a new authenticator object."""
        return IndeedSponsoredJobsAuthenticator.create_multiemployerauth_for_stream(self)
    
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property("name", th.StringType),
        th.Property(
            "id",
            th.StringType
        ),
        th.Property(
            "name",
            th.StringType,
        ),
    ).to_dict()
    
    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
                "_sdc_employer_id": record["id"],
                }

class Campaigns(IndeedSponsoredJobsStream):
    """Campaigns per Employer"""
    name = "campaigns"
    path = "/v1/campaigns"
    primary_keys = ["Id"]
    records_jsonpath = "$.['Campaigns'][*]"
    replication_key = None
    parent_stream_type = Employers
    schema = th.PropertiesList(
            th.Property("Name", th.StringType),
            th.Property("Id", th.StringType),
            th.Property("Status", th.StringType),
            th.Property("_sdc_employer_id", th.StringType),
            ).to_dict()
    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
                "_sdc_employer_id": record["id"],
                "_sdc_campaign_id": record["Id"],
                }

class CampaignPerformanceStats(IndeedSponsoredJobsStream):
    """Campaign Performance per Campaign"""
    name = "campaign_performance_stats"
    path = "/v1/campaigns/{_sdc_campaign_id}/stats"
    primary_keys = ["Id"]
    records_jsonpath = "$.['entries'][*]"
    replication_key = None
    parent_stream_type = Campaigns
    schema = th.PropertiesList(
            th.Property("Name", th.StringType),
            th.Property("Id", th.StringType),
            th.Property("Date", th.StringType),
            th.Property("Clicks", th.IntegerType),
            th.Property("Impressions", th.IntegerType),
            th.Property("Conversions", th.IntegerType),
            th.Property("CurrencyCode", th.StringType),
            th.Property("Cost", th.NumberType),
            th.Property("OrganicClicks", th.IntegerType),
            th.Property("OrganicImpressions", th.IntegerType),
            th.Property("Applystarts", th.IntegerType),
            th.Property("OrganicApplystarts", th.IntegerType),
            th.Property("_sdc_employer_id", th.StringType),
            th.Property("_sdc_campaign_id", th.StringType),
            ).to_dict()

class CampaignBudget(IndeedSponsoredJobsStream):
    """Campaign Budget per Campaign"""
    name = "campaign_budget"
    path = "/v1/campaigns/{_sdc_campaign_id}/budget"
    primary_keys = ["_sdc_campaign_id"]
    records_jsonpath = "$.['data']"
    replication_key = None
    parent_stream_type = Campaigns
    schema = th.PropertiesList(
            th.Property("budgetMonthlyLimit", th.NumberType),
            th.Property("_sdc_employer_id", th.StringType),
            th.Property("_sdc_campaign_id", th.StringType),
            ).to_dict()

class CampaignInfo(IndeedSponsoredJobsStream):
    """Campaign Info per Campaign"""
    name = "campaign_info"
    path = "/v1/campaigns/{_sdc_campaign_id}"
    primary_keys = ["Id"]
    records_jsonpath = "$.['data']"
    replication_key = None
    parent_stream_type = Campaigns
    schema = th.PropertiesList(
            th.Property("Name", th.StringType),
            th.Property("Id", th.StringType),
            th.Property("Type", th.StringType),
            th.Property("Status", th.StringType),
            th.Property("CurrencyCode", th.StringType),
            th.Property("TrackingToken", th.StringType),
            th.Property("Objective", th.ObjectType(
                                    th.Property("description", th.StringType),
                                    th.Property("objectiveType", th.StringType),
                                    )),
            th.Property("NonSpendingReasons", th.ArrayType(th.StringType)),
            th.Property("SpendingChannels", th.IntegerType),
            th.Property("_sdc_employer_id", th.StringType),
            th.Property("_sdc_campaign_id", th.StringType),
            ).to_dict()
