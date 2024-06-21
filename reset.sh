echo "Dropping"
dropdb pricelist -f
echo "Creating"
createdb pricelist
echo "Populating"
psql -d pricelist < pricelist_staging.psql
