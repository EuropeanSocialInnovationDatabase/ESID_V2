Despite the increasing policy and scholarly interest on SI, one of the barriers for better understanding of the concept is the availability of data. Unlike other forms of innovation for which there are mature data sources (e.g. patents, publications, financial data, etc.) that have been developed and utilised for decades, there has not been a comprehensive and reliable data source for SI. While there have been a number of previous attempts to create a data source of SI, mainly funded by the EU, they were mainly limited in size, scope and data collection methods.

This gap motivated us to create ESID which was first constructed as part of the EU-funded KNOWMAK project and is currently a part of the RISIS project. ESID utilises semi-automatic advanced machine learning and natural language processing techniques to collect information about social innovation projects from the publicly available information on the web. ESID also uses some limited human annotation to train the machine learning models and to ensure the quality and the integrity of the data. Thanks to its innovative method, ESID offers the advantage of being much more comprehensive in size and themes it covers, a flexible conceptual structure, richer and more consistent information, and sustainability as it requires much less human involvement.

Currently, the main entity in ESID is SI projects. It also contains a number of project features, main ones being their scores on four SI criteria (see below), location (country, city, NUTS regions, approximate coordinates), topic (Key Enabling Technologies and Societal Grand Challenges adapted from H2020 priority areas), a short summary, URL, source from which we identified. In the first phase, ESID identified SI projects from over 90 known sources (including previous limited databases, membership registers, prizes nominations, appearance in directly related media, etc.). Subsequently, we crawled websites and other information on the web. By using this large corpus, we then verified, extended and enriched the information on SI projects.

As discussed above, SI has a multitude of vigorously debated definitions. As humans do not have an agreement on the exact meaning of the concept, it was challenging to train a machine learning model on SI. To overcome this challenge, we conducted a literature review based on previous work and identified four main elements all definitions use in different combinations and emphasis (Caulier-Grice et al., 2012, Choi and Majumdar, 2015, Dawson and Daniel, 2010, Ettorre et al., 2014, Grimm et al., 2013, Harrisson, 2013, Jessop et al., 2013, van der Have and Rubalcaba, 2016, Edwards-Schachter and Wallace, 2017):

Objectives: Social innovations satisfy societal needs - including the needs of particular social groups (or aim at social value creation) - that are usually not met by conventional innovative activity (c.f. "economic innovation"), either as a goal or end-product. As a result, social innovation does not produce conventional innovation outputs such as patents and publications.

Actors and actor interactions: Innovations that are created by actors who usually are not involved in "economic innovation," including informal actors, are also defined as social innovation. Some authors stress that innovations must involve predominantly new types of social interactions that achieve common goals and/or innovations that rely on trust rather than mutual-benefit relationships. Similarly, some authors consider innovations that involve different action and diffusion processes but ultimately result in social progress as social innovation.

Outputs/Outcomes: Early definitions of social innovation strongly relate it with the production of social technologies (c.f. innovation employing only "physical technologies") or "intangible innovation." This is complemented by some definitions, which indicate that social innovation changes the attitudes, behaviours and perceptions of the actors involved. Some other definitions stress the public good that social innovation creates. Social innovation is often associated with long-term institutional/cultural change.

Innovativeness: The majority of these definitions emphasise novelty and innovativeness as essential characteristics of social or other types of innovation, while there are others (Rogers, 2010) who relieve this criteria for social innovation. The novelty criteria are often seen as one of the key distinguishing factors between social innovation and social entrepreneurship (Cunha et al., 2015, Phillips et al., 2015). Similarly, most definitions share other essential characteristics of the classical OECD definition of ("technological product and process") innovation, namely involving a distinguishable practical activity (i.e. idea to be implemented) and resulting in new products, processes, services and models (OECD and EUROSTAT, 2005).

Rather than choosing a particular definition, ESID scores each project for the above four criteria on a three-point scale (0 no indication of the criteria, 1 partially satisfies, 2 fully satisfies). This enables its users to construct their own definition by filtering for the four scores. We also introduced a total score which is the sum of the four criteria and ranges between 0 and 8.

We experimented a number of different machine learning techniques for predicting the each of the criteria by analysing the text contained on the web. The best performing set of models utilised the state of the art Bidirectional Encoder Representations from Transformers (BERT). BERT models performed about 90% (F1 Measure) on average on the evaluation data coded by humans. This is exceptionally high performance, considering the fact that the human coders agree on about 85% (inter-annotater agreement).

Currently ESID contains 11,441 projects from 153 countries. Some of these projects are "negative examples" (e.g. scoring 0 for all four criteria) required for machine learning models. Furthermore, some projects do not have complete information (e.g. location not identified as yet or topics not matched). 

The ESID app can be found at https://esid.shinyapps.io/ESID/ and shows only projects where total is greater than 0.

As part of RISIS 2, ESID will be improved in three main areas:

Expansion: We aim to increase the number of projects to tens of thousands.

Extension: New Features, such as aims and impact of projects, will be added.

Dynamic retrieval: We aim to collect web data in regular intervals to be able to track the changes in projects.

More information on ESID and its methodology can be found at https://rcf.risis2.eu/dataset/13/metadata

A policy brief on the analysis shown in this tool can be found at https://zenodo.org/record/5727109/#.Yjs-vurP02w


Related published work:
MILOSEVIC, N., GOK, A. & NENADIC, G. Classification of Intangible Social Innovation Concepts. In: SILBERZTEIN, M., ATIGUI, F., KORNYSHOVA, E., MÉTAIS, E. & MEZIANE, F., eds. Natural Language Processing and Information Systems, 2018// 2018 Cham. Springer International Publishing, 407-418.
MILOSEVIC, N., GOK, A. & NENADIC, G. Classification of Intangible Social Innovation Concepts. In: SILBERZTEIN, M., ATIGUI, F., KORNYSHOVA, E., MÉTAIS, E. & MEZIANE, F., eds. Natural Language Processing and Information Systems, 2018// 2018 Cham. Springer International Publishing, 407-418.




