package it.elasticsearch.analyzer;

import static org.fest.assertions.Assertions.assertThat;
import it.elasticsearch.models.ComputedHappiness;

import java.io.IOException;
import java.util.HashMap;
import java.util.Properties;

import org.junit.Test;

public class HedonometerAnalyzerTest {

	private String firstWord = "hello";
	private String secondWord = "world";
	private double firstHappiness = 7.0;
	private double secondHappiness = 2.0;
	private double defaultHappiness = 5.0;

	@Test
	public void shouldComputeHappinessReturnNullWhenWordsHappinessNull() throws IOException {
		// given
		String tweetText = firstWord + " " + secondWord;
		HashMap<String, Double> wordsHappiness = null;

		HedonometerAnalyzer hedonometer = new HedonometerAnalyzer();

		// when
		ComputedHappiness happiness = hedonometer.computeHappiness(tweetText, wordsHappiness);

		// then
		assertThat(happiness).isNull();
	}

	@Test
	public void shouldComputeHappinessWorkWithValidWordsAndNotOnlyRelevant() throws IOException {
		// given
		String tweetText = firstWord + " " + secondWord;
		HashMap<String, Double> wordsHappiness = new HashMap<String, Double>();
		wordsHappiness.put(firstWord, firstHappiness);
		wordsHappiness.put(secondWord, secondHappiness);

		double computedHappiness = (firstHappiness + secondHappiness) / 2;
		double computedRelevance = 1.0;
		HedonometerAnalyzer happinessAnalyzer = new HedonometerAnalyzer();

		// when
		ComputedHappiness happiness = happinessAnalyzer.computeHappiness(tweetText, wordsHappiness);

		// then
		assertThat(happiness).isNotNull();
		assertThat(happiness.getScore()).isEqualTo(computedHappiness);
		assertThat(happiness.getRelevance()).isEqualTo(computedRelevance);
	}

	@Test
	public void shouldComputeHappinessWorkWithUnvalidWordsAndNotOnlyRelevant() throws IOException {
		// given
		String tweetText = secondWord + " " + secondWord;
		HashMap<String, Double> wordsHappiness = new HashMap<String, Double>();
		wordsHappiness.put(firstWord, firstHappiness);

		double computedRelevance = 0.0;
		HedonometerAnalyzer hedonometer = new HedonometerAnalyzer();

		// when
		ComputedHappiness happiness = hedonometer.computeHappiness(tweetText, wordsHappiness);

		// then
		assertThat(happiness).isNotNull();
		assertThat(happiness.getScore()).isEqualTo(defaultHappiness);
		assertThat(happiness.getRelevance()).isEqualTo(computedRelevance);
	}

	@Test
	public void shouldComputeHappinessWorkWithValidAndUnvalidWordsAndNotOnlyRelevant() throws IOException {
		// given
		String tweetText = firstWord + " " + secondWord;
		HashMap<String, Double> wordsHappiness = new HashMap<String, Double>();
		wordsHappiness.put(firstWord, firstHappiness);

		double computedHappiness = (firstHappiness + defaultHappiness) / 2;
		double computedRelevance = 0.5;
		HedonometerAnalyzer hedonometer = new HedonometerAnalyzer();

		// when
		ComputedHappiness happiness = hedonometer.computeHappiness(tweetText, wordsHappiness);

		// then
		assertThat(happiness).isNotNull();
		assertThat(happiness.getScore()).isEqualTo(computedHappiness);
		assertThat(happiness.getRelevance()).isEqualTo(computedRelevance);
	}

	@Test
	public void shouldComputeHappinessWorkWithValidWordsAndOnlyRelevant() throws IOException {
		// given
		String tweetText = firstWord + " " + secondWord;
		HashMap<String, Double> wordsHappiness = new HashMap<String, Double>();
		wordsHappiness.put(firstWord, firstHappiness);
		wordsHappiness.put(secondWord, secondHappiness);

		double computedHappiness = (firstHappiness + secondHappiness) / 2;
		double computedRelevance = 1.0;
		HedonometerAnalyzer hedonometer = new HedonometerAnalyzer();

		Properties properties = new Properties();
		properties.put(HedonometerAnalyzer.PARAM_ONLYRELEVANT, "true");
		hedonometer.initialize(properties);

		// when
		ComputedHappiness happiness = hedonometer.computeHappiness(tweetText, wordsHappiness);

		// then
		assertThat(happiness).isNotNull();
		assertThat(happiness.getScore()).isEqualTo(computedHappiness);
		assertThat(happiness.getRelevance()).isEqualTo(computedRelevance);
	}

	@Test
	public void shouldComputeHappinessWorkWithUnvalidWordsAndOnlyRelevant() throws IOException {
		// given
		String tweetText = secondWord + " " + secondWord;
		HashMap<String, Double> wordsHappiness = new HashMap<String, Double>();
		wordsHappiness.put(firstWord, firstHappiness);

		double computedHappiness = 0.0;
		double computedRelevance = 0.0;
		HedonometerAnalyzer hedonometer = new HedonometerAnalyzer();

		Properties properties = new Properties();
		properties.put(HedonometerAnalyzer.PARAM_ONLYRELEVANT, "true");
		hedonometer.initialize(properties);

		// when
		ComputedHappiness happiness = hedonometer.computeHappiness(tweetText, wordsHappiness);

		// then
		assertThat(happiness).isNotNull();
		assertThat(happiness.getScore()).isEqualTo(computedHappiness);
		assertThat(happiness.getRelevance()).isEqualTo(computedRelevance);
	}

	@Test
	public void shouldComputeHappinessWorkWithValidAndUnvalidWordsAndOnlyRelevant() throws IOException {
		// given
		String tweetText = firstWord + " " + secondWord;
		HashMap<String, Double> wordsHappiness = new HashMap<String, Double>();
		wordsHappiness.put(firstWord, firstHappiness);

		double computedHappiness = firstHappiness;
		double computedRelevance = 0.5;
		HedonometerAnalyzer hedonometer = new HedonometerAnalyzer();

		Properties properties = new Properties();
		properties.put(HedonometerAnalyzer.PARAM_ONLYRELEVANT, "true");
		hedonometer.initialize(properties);

		// when
		ComputedHappiness happiness = hedonometer.computeHappiness(tweetText, wordsHappiness);

		// then
		assertThat(happiness).isNotNull();
		assertThat(happiness.getScore()).isEqualTo(computedHappiness);
		assertThat(happiness.getRelevance()).isEqualTo(computedRelevance);
	}

	@Test
	public void shouldComputeHappinessWorkIgnoringCase() throws IOException {
		// given
		String tweetText = firstWord + " " + secondWord.toUpperCase();
		HashMap<String, Double> wordsHappiness = new HashMap<String, Double>();
		wordsHappiness.put(firstWord, firstHappiness);

		double computedHappiness = (firstHappiness + defaultHappiness) / 2;
		double computedRelevance = 0.5;
		HedonometerAnalyzer hedonometer = new HedonometerAnalyzer();

		// when
		ComputedHappiness happiness = hedonometer.computeHappiness(tweetText, wordsHappiness);

		// then
		assertThat(happiness).isNotNull();
		assertThat(happiness.getScore()).isEqualTo(computedHappiness);
		assertThat(happiness.getRelevance()).isEqualTo(computedRelevance);
	}
}
