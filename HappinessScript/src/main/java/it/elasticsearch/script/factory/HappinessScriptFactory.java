package it.elasticsearch.script.factory;

import it.elasticsearch.script.HappinessScript;

import java.io.FileInputStream;
import java.io.IOException;
import java.util.Map;
import java.util.Properties;

import org.elasticsearch.ElasticSearchIllegalArgumentException;
import org.elasticsearch.common.Nullable;
import org.elasticsearch.common.logging.ESLogger;
import org.elasticsearch.common.logging.Loggers;
import org.elasticsearch.script.ExecutableScript;
import org.elasticsearch.script.NativeScriptFactory;

public class HappinessScriptFactory implements NativeScriptFactory {

	protected final ESLogger logger = Loggers.getLogger("happiness.script");
	public static final String PROPERTIES_FILENAME = "/etc/elasticsearch/happiness.properties";
	public static final String PARAM_PROPERTIES = "properties";

	public Properties getScriptProperties(@Nullable Map<String, Object> params) throws IOException {
		String fileName = PROPERTIES_FILENAME;

		if (params != null) {
			String paramsFilename = (String) params.get(PARAM_PROPERTIES);
			if (paramsFilename != null) {
				fileName = paramsFilename;
			}
		}

		Properties properties = new Properties();
		properties.load(new FileInputStream(fileName));
		return properties;
	}

	@Override
	public ExecutableScript newScript(@Nullable Map<String, Object> params) {
		try {
			Properties properties = getScriptProperties(params);
			return new HappinessScript(properties);
		} catch (IOException e) {
			logger.error("Error while getting HappinessScript class: {}", e);
			throw new ElasticSearchIllegalArgumentException();
		}
	}
}
