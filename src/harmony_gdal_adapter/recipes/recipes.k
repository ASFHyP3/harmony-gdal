import schema

recipes = [
        schema.RecipeMetadata {
                path = "nisar.k"
                file_match_pattern = "\.h5$"
                accepted_collection_shortnames = [
                       "NISAR_L3_SME2_PROVISIONAL_V1"
                       "NISAR_L2_GUNW_PROVISIONAL_V1"
                       "NISAR_L2_GOFF_PROVISIONAL_V1"
                       "NISAR_L2_GCOV_PROVISIONAL_V1"
                       "NISAR_L3_SME2_BETA_V1"
                       "NISAR_L2_GUNW_BETA_V1"
                       "NISAR_L2_GOFF_BETA_V1"
                       "NISAR_L2_GCOV_BETA_V1"
                ]
        }
]
