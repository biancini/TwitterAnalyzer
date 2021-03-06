package it.elasticsearch.script.facet;

import static org.elasticsearch.common.collect.Lists.newArrayList;
import it.elasticsearch.models.ComputedHappiness;
import it.elasticsearch.utilities.FacetParamsManager;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.elasticsearch.client.Client;
import org.elasticsearch.common.Strings;
import org.elasticsearch.common.bytes.BytesReference;
import org.elasticsearch.common.bytes.HashedBytesArray;
import org.elasticsearch.common.io.stream.StreamInput;
import org.elasticsearch.common.io.stream.StreamOutput;
import org.elasticsearch.common.xcontent.XContentBuilder;
import org.elasticsearch.common.xcontent.XContentBuilderString;
import org.elasticsearch.script.ExecutableScript;
import org.elasticsearch.script.ScriptService;
import org.elasticsearch.search.facet.Facet;
import org.elasticsearch.search.facet.InternalFacet;

public class HappinessInternalFacet extends InternalFacet implements HappinessFacet {
	public static final String TYPE_FIELD = "_type";
	public static final String CLIENT_PARAM = "_client";

	public static final String FACET_TYPE = "facet";

	private static final BytesReference STREAM_TYPE = new HashedBytesArray(
			Strings.toUTF8Bytes(HappinessFacet.TYPE));

	private ScriptService scriptService = null;
	private Client client = null;
	private Object facet = null;
	private Map<String, Object> reduceScript = null;

	private HappinessInternalFacet(ScriptService scriptService, Client client) {
		this.scriptService = scriptService;
		this.client = client;
	}

	public HappinessInternalFacet(String name, Object facet, Map<String, Object> reduceScript,
			ScriptService scriptService, Client client) {

		super(name);

		this.scriptService = scriptService;
		this.client = client;
		this.facet = facet;
		this.reduceScript = reduceScript;
	}

	public static void registerStreams(ScriptService scriptService, Client client) {
		Streams.registerStream(new ScriptFacetStream(scriptService, client), STREAM_TYPE);
	}

	@Override
	public BytesReference streamType() {
		return STREAM_TYPE;
	}

	@Override
	@SuppressWarnings("unchecked")
	public Facet reduce(ReduceContext reduceContext) {
		List<Object> facetObjects = newArrayList();

		for (Facet facet : reduceContext.facets()) {
			HappinessInternalFacet mapReduceFacet = (HappinessInternalFacet) facet;

			if (mapReduceFacet.facet() instanceof ComputedHappiness) {
				ComputedHappiness curFacet = (ComputedHappiness) mapReduceFacet.facet();
				facetObjects.add(curFacet);
			} else {
				List<ComputedHappiness> curFacet = (List<ComputedHappiness>) mapReduceFacet.facet();
				facetObjects.addAll(curFacet);
			}
		}

		HappinessInternalFacet firstFacet = ((HappinessInternalFacet) reduceContext.facets().get(0));

		Object facet = null;
		if (firstFacet.reduceScript != null) {
			Map<String, Object> additionalParams = new HashMap<String, Object>();
			additionalParams.put(FACET_TYPE, facetObjects);
			additionalParams.put(CLIENT_PARAM, client);

			ExecutableScript execScript = FacetParamsManager.getExecutableScript(firstFacet.reduceScript,
					additionalParams, scriptService);
			facet = execScript.unwrap(execScript.run());
		} else {
			facet = facetObjects;
		}

		return new HappinessInternalFacet(firstFacet.getName(), facet, reduceScript, scriptService, client);
	}

	@Override
	public String getType() {
		return HappinessFacet.TYPE;
	}

	@Override
	public void readFrom(StreamInput in) throws IOException {
		super.readFrom(in);

		reduceScript = in.readMap();
		facet = in.readGenericValue();
	}

	@Override
	public void writeTo(StreamOutput out) throws IOException {
		super.writeTo(out);

		out.writeMap(reduceScript);
		out.writeGenericValue(facet);
	}

	@Override
	public Object facet() {
		return facet;
	}

	@Override
	public Object getFacet() {
		return facet();
	}

	static final class Fields {
		static final XContentBuilderString _TYPE = new XContentBuilderString(TYPE_FIELD);
		static final XContentBuilderString FACET = new XContentBuilderString(FACET_TYPE);
	}

	@Override
	public XContentBuilder toXContent(XContentBuilder builder, Params params) throws IOException {
		builder.startObject(getName());
		builder.field(Fields._TYPE, HappinessFacet.TYPE);
		builder.field(Fields.FACET, facet);
		builder.endObject();
		return builder;
	}

	public static HappinessInternalFacet readMapReduceFacet(StreamInput in, ScriptService scriptService,
			Client client) throws IOException {
		HappinessInternalFacet facet = new HappinessInternalFacet(scriptService, client);
		facet.readFrom(in);
		return facet;
	}

	private static class ScriptFacetStream implements InternalFacet.Stream {
		private ScriptService scriptService = null;
		private Client client = null;

		public ScriptFacetStream(ScriptService scriptService, Client client) {
			this.scriptService = scriptService;
			this.client = client;
		}

		@Override
		public Facet readFacet(StreamInput in) throws IOException {
			return HappinessInternalFacet.readMapReduceFacet(in, scriptService, client);
		}

	}
}