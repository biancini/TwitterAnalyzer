package fr.twitteranalyzer.elastic;

import java.util.Date;

import org.elasticsearch.client.Client;

import fr.twitteranalyzer.Analyzer;
import fr.twitteranalyzer.exceptions.AnalyzerException;

public abstract class ElasticAnalyzerImpl implements Analyzer {

	public static final String CUSTERNAME = "frenchtweets";
	public static final String ELASTICSEARCH_HOST = "localhost";
	public static final int ELASTICSEARCH_PORT = 9300;

	public static final String INDEXNAME = "twitter";
	public static final String TWEETSTYPE = "tweets";
	public static final String BYPERSONTYPE = "byperson";

	protected static Client client = null;

	public static Client getClient() {
		return client;
	}

	public abstract void runAnalysis(Date from, Date to) throws AnalyzerException;

}
