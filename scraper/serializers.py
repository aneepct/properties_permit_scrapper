from rest_framework import serializers
from .models import Permit, ScraperRun


class PermitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permit
        fields = '__all__'


class ScraperRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScraperRun
        fields = '__all__'


class ScraperRunCreateSerializer(serializers.Serializer):
    """Serializer for starting a new scraper run"""
    cities = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        help_text="List of cities to scrape (nyc, chicago, la, sf). If empty, all cities will be scraped."
    )
    force_rescrape = serializers.BooleanField(
        default=False,
        help_text="Force rescrape even if recent data exists"
    )