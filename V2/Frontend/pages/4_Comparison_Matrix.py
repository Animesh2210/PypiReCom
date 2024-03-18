import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import requests
from constants import * 
import graphviz
from PIL import Image
from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, px
from htbuilder.funcs import rgba, rgb

st.set_page_config(
    page_title="PypiReCom"
)

def search_package(search_url):
    return requests.get(search_url).json()

def layout(*args):

    style = """
    <style>
      # MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
     .stApp { bottom: 105px; }
    </style>
    """

    style_div = styles(
        position="fixed",
        left=0,
        bottom=0,
        margin=px(0, 0, 0, 0),
        width=percent(100),
        color="White",
        text_align="center",
        height="auto",
        opacity=1
    )

    style_hr = styles(
        display="block",
        margin=px(8, 8, "auto", "auto"),
        border_style="inset",
        border_width=px(2)
    )

    body = p()
    foot = div(
        style=style_div
    )(
        hr(
            style=style_hr
        ),
        body
    )

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)

        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)


def footer():
    myargs = [
        """
        <p>
        Made with ❤️ by 
        <a href="https://www.linkedin.com/in/bioenable" target="_blank">Dr. Shyam Sundaram</a>,
        <a href="https://www.linkedin.com/in/animesh2210" target="_blank">Animesh Verma</a> &
        <a href="https://www.linkedin.com/in/avs-sridhar-8b9904176/" target="_blank">Sridhar Aluru</a>
        </p>
        """
    ]
    layout(*myargs)

def generate_search_url(search_text):
    return api_endpoint + '/comparison_metric?Search_Text=' + search_text

def set_search_state(text, exact=0):
    st.session_state['search_text'] = text
    st.session_state['search_exact'] = exact

def main():
    #basic page
    if 'search_text' not in st.session_state:
        st.session_state['search_text'] = ''
    if 'search_exact' not in st.session_state:
        st.session_state['search_exact'] = 0

    footer()
    # with st.sidebar:
    #     st.header('Contributers')
    #     st.markdown("""
    #     **Dr. Shyam Sundaram**
    #     - [LinkedIn](https://www.linkedin.com/in/bioenable)
    #     - [Github](https://github.com/drshyamsundaram)
    #     """)
    #     st.markdown("""
    #     **Animesh Verma**
    #     - [LinkedIn](https://www.linkedin.com/in/animesh2210)
    #     - [Github](https://github.com/Animesh2210)
    #     """)
    st.image(Image.open('PypiReCom_Logo.png'),width=300)
    st.subheader("Compare the results!")
    with st.form(key='Search_Package_Form'):
        nav1,nav2 = st.columns([5,1])

        with nav1:
            search_text = st.text_input("Search for:", st.session_state['search_text'])

        with nav2:
            # st.text("Search")
            st.text('')
            search_button = st.form_submit_button(label='Search')
        
    #result
    if search_button:
        col1, col2 = st.columns([2, 3])

        search_url = generate_search_url(search_text)
        response = search_package(search_url)

        with col1:
            st.subheader("Pip Result")
            package_names = (response['Pip'])['result']
            # st.write(package_names)
            for package_name in package_names:
                st.write(package_name)

            st.divider()
            st.subheader("Confusion Matrix")
            positive, negative = st.columns(2)
            with positive: 
                st.metric(label="True Positive", value="100%")
                st.metric(label="False Positive", value=0)
            
            with negative: 
                st.metric(label="True Negative", value=0)
                st.metric(label="False Negative", value=0)

        result = response['Pypirecom']
        if type(result) == str:
            st.write(result)
            st.session_state['search_exact'] = 0
        # elif 'Suggested Packages' in result:
        #     st.write('We can not find a direct match. Are you searching for something like this?')
        #     # print(result['Suggested Packages'])
        #     for suggestion in result['Suggested Packages']:
        #         # search_texts.append((' '.join(suggestion.split('_'))))
        #         st.button(label=(' '.join(suggestion.split('_')).title()), on_click=set_search_state, args=[' '.join(suggestion.split('_')).title()])
        #     st.button(label='Not happy :(. Instead search for ' + search_text, on_click=set_search_state, args=[search_text.title(),1])
        else:
            with col2:
                st.subheader("PypiReCom Result")
                st.success("Showing results for " + search_text)
                st.subheader("Knowledge Graph")
                graph = graphviz.Digraph()
                graph.attr('node', size = '2,2')
                for package_dependency in result['Package_Dependency']:
                    graph.node(package_dependency['package'],shape='doublecircle')
                    graph.edge(package_dependency['package'],package_dependency['dependency'],label='has_dependency')
                for package_license in result['Package_License']:
                    graph.edge(package_license['package'],package_license['license'],label='has_license')
                for package_language in result['Package_Language']:
                    graph.edge(package_language['package'],package_language['programming_language'],label='used_language')
                # try:
                #     json_file = requests.get(api_endpoint + '/get_graph_file?Search_Text=' + search_text).content
                #     if json_file.decode('ascii') == 'Internal Server Error':
                #         raise Exception('Json file not available.')
                #     st.download_button("Download Graph Json",data=json_file,file_name=search_text+'_Graph.json')
                # except:
                #     pass
                # try:
                #     gml_file = requests.get(api_endpoint + '/get_gml_file?Search_Text=' + search_text).content
                #     if gml_file.decode('ascii') == 'Internal Server Error':
                #         raise Exception('GML file not available.')
                #     st.download_button("Download Graph GML",data=gml_file,file_name=search_text+'_Graph.gml')
                # except Exception as e:
                #     pass
                st.write(graph)
                # st.download_button("Download Graph Image",data=graph.render(format='png'))
                pkg_name,dependency_count,dev_status = st.columns(3)

                pkg_name.write("Package Name")
                dependency_count.write("Total Dependencies")
                dev_status.write("Development Status")
                packages = result['result']
                for package in packages:
                    pkg_name,dependency_count,dev_status = st.columns(3)
                    pkg_name.write(package['v_id'])
                    dependency_count.write(result['Package_Dependency_Count'].get(package['v_id']))
                    dev_status.write(package['attributes']['dev_status'])
                st.session_state['search_exact'] = 0

main()