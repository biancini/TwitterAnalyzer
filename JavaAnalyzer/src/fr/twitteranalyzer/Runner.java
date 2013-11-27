package fr.twitteranalyzer;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

import fr.twitteranalyzer.elastic.ByPersonAnalyzer;
import fr.twitteranalyzer.exceptions.AnalyzerException;

//import fr.twitteranalyzer.mapreduce.ByPersonAnalyzer;

public class Runner {

	/**
	 * @param args
	 * @throws ParseException
	 */
	public static void main(String[] args) throws ParseException {
		try {
			ByPersonAnalyzer analyzer = new ByPersonAnalyzer();

			SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");

			Date fromDate = Calendar.getInstance().getTime();
			fromDate = sdf.parse("2013-11-26");

			Date toDate = Calendar.getInstance().getTime();
			toDate = sdf.parse("2014-01-26");

			analyzer.runAnalysis(fromDate, toDate);
		} catch (AnalyzerException e) {
			System.err.println(e.getMessage());
			e.printStackTrace();
		}
	}

}
