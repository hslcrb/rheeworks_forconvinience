/*
 * StudyAI - MV (Minimum Viable)
 * Simple AI Chat Application using GTK3 + libcurl + cJSON
 * Rheehose (Rhee Creative) 2008-2026
 * Licensed under Apache-2.0
 */

#include <gtk/gtk.h>
#include <curl/curl.h>
#include <string.h>
#include <stdlib.h>
#include "cJSON.h"

// TODO: Replace with your actual Mistral API Key
#define MISTRAL_API_KEY "OBfwuYKEEUFvjh5bLt18XOcVIpTYFHVQ"
#define MISTRAL_API_URL "https://api.mistral.ai/v1/chat/completions"
#define MODEL_NAME "mistral-small-latest"

GtkWidget *text_view;
GtkWidget *entry;
GtkWidget *send_btn;
GtkWidget *spinner;
GtkTextBuffer *buffer;
int is_dark_mode = 0;

struct MemoryStruct {
  char *memory;
  size_t size;
};

static size_t WriteMemoryCallback(void *contents, size_t size, size_t nmemb, void *userp) {
  size_t realsize = size * nmemb;
  struct MemoryStruct *mem = (struct MemoryStruct *)userp;
  char *ptr = realloc(mem->memory, mem->size + realsize + 1);
  if(!ptr) return 0; // Out of memory
  mem->memory = ptr;
  memcpy(&(mem->memory[mem->size]), contents, realsize);
  mem->size += realsize;
  mem->memory[mem->size] = 0;
  return realsize;
}

void append_text(const char *text, const char *tag) {
    GtkTextIter end;
    gtk_text_buffer_get_end_iter(buffer, &end);
    gtk_text_buffer_insert_with_tags_by_name(buffer, &end, text, -1, tag, NULL);
    gtk_text_buffer_insert(buffer, &end, "\n\n", -1);
    
    // Auto scroll to bottom
    GtkTextMark *mark = gtk_text_buffer_create_mark(buffer, NULL, &end, FALSE);
    gtk_text_view_scroll_to_mark(GTK_TEXT_VIEW(text_view), mark, 0.0, TRUE, 0.0, 1.0);
}

void send_mistral_request(const char *user_input) {
    CURL *curl;
    CURLcode res;
    struct MemoryStruct chunk;
    chunk.memory = malloc(1);
    chunk.size = 0;

    curl = curl_easy_init();
    if(curl) {
        cJSON *root = cJSON_CreateObject();
        cJSON_AddStringToObject(root, "model", MODEL_NAME);
        cJSON *messages = cJSON_CreateArray();
        cJSON *msg = cJSON_CreateObject();
        cJSON_AddStringToObject(msg, "role", "user");
        cJSON_AddStringToObject(msg, "content", user_input);
        cJSON_AddItemToArray(messages, msg);
        cJSON_AddItemToObject(root, "messages", messages);
        
        char *json_str = cJSON_PrintUnformatted(root);
        
        struct curl_slist *headers = NULL;
        headers = curl_slist_append(headers, "Content-Type: application/json");
        char auth_header[256];
        snprintf(auth_header, sizeof(auth_header), "Authorization: Bearer %s", MISTRAL_API_KEY);
        headers = curl_slist_append(headers, auth_header);

        curl_easy_setopt(curl, CURLOPT_URL, MISTRAL_API_URL);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_str);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteMemoryCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&chunk);

        append_text("🤖 Thinking...", "system");
        
        // Blocking call (for simple MVP) - in real app, use async thread
        // Update: MVP requirement is "very simple GUI", so blocking is acceptable but will freeze UI.
        // To prevent total freeze, we run UI loop... but for C GTK without threads complex.
        // Let's stick to blocking for MVP as requested "Simple".
        while (gtk_events_pending()) gtk_main_iteration();

        res = curl_easy_perform(curl);
        
        if(res != CURLE_OK) {
            char error_msg[256];
            snprintf(error_msg, sizeof(error_msg), "Error: %s", curl_easy_strerror(res));
            append_text(error_msg, "error");
        } else {
            cJSON *json = cJSON_Parse(chunk.memory);
            if (json) {
                cJSON *choices = cJSON_GetObjectItemCaseSensitive(json, "choices");
                if (cJSON_IsArray(choices)) {
                    cJSON *choice = cJSON_GetArrayItem(choices, 0);
                    cJSON *message = cJSON_GetObjectItemCaseSensitive(choice, "message");
                    cJSON *content = cJSON_GetObjectItemCaseSensitive(message, "content");
                    if (cJSON_IsString(content)) {
                        append_text(content->valuestring, "bot");
                    }
                } else {
                     append_text("Error: Invalid response format.", "error");
                }
                cJSON_Delete(json);
            } else {
                append_text("Error: Failed to parse JSON.", "error");
            }
        }

        curl_easy_cleanup(curl);
        curl_slist_free_all(headers);
        cJSON_Delete(root);
        free(json_str);
        free(chunk.memory);
    }
}

void on_send_clicked(GtkWidget *widget, gpointer data) {
    const char *text = gtk_entry_get_text(GTK_ENTRY(entry));
    if (strlen(text) > 0) {
        append_text(text, "user");
        char *input_copy = strdup(text);
        gtk_entry_set_text(GTK_ENTRY(entry), "");
        send_mistral_request(input_copy);
        free(input_copy);
    }
}

void apply_css(GtkWidget *widget, GtkStyleProvider *provider) {
    gtk_style_context_add_provider(gtk_widget_get_style_context(widget), provider, GTK_STYLE_PROVIDER_PRIORITY_USER);
    if (GTK_IS_CONTAINER(widget)) {
        gtk_container_forall(GTK_CONTAINER(widget), (GtkCallback)apply_css, provider);
    }
}

void set_theme(int dark) {
    GtkCssProvider *provider = gtk_css_provider_new();
    const char *css;
    if (dark) {
        css = "* { background-color: #1e1e1e; color: #ffffff; } entry { background-color: #2d2d2d; color: #ffffff; } button { background-color: #3e3e3e; color: #ffffff; } textview text { background-color: #1e1e1e; color: #ffffff; }";
    } else {
        css = "* { background-color: #f0f0f0; color: #000000; } entry { background-color: #ffffff; color: #000000; } button { background-color: #e0e0e0; color: #000000; } textview text { background-color: #ffffff; color: #000000; }";
    }
    gtk_css_provider_load_from_data(provider, css, -1, NULL);
    
    GdkScreen *screen = gdk_screen_get_default();
    gtk_style_context_add_provider_for_screen(screen, GTK_STYLE_PROVIDER(provider), GTK_STYLE_PROVIDER_PRIORITY_APPLICATION);
    g_object_unref(provider);
}

void on_toggle_theme(GtkWidget *widget, gpointer data) {
    is_dark_mode = !is_dark_mode;
    set_theme(is_dark_mode);
    gtk_button_set_label(GTK_BUTTON(widget), is_dark_mode ? "☀️ Light Mode" : "🌙 Dark Mode");
}

int main(int argc, char *argv[]) {
    gtk_init(&argc, &argv);

    GtkWidget *window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(window), "StudyAI - MV");
    gtk_window_set_default_size(GTK_WINDOW(window), 400, 600);
    g_signal_connect(window, "destroy", G_CALLBACK(gtk_main_quit), NULL);

    GtkWidget *vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 5);
    gtk_container_add(GTK_CONTAINER(window), vbox);
    gtk_container_set_border_width(GTK_CONTAINER(window), 10);

    // Header
    GtkWidget *header_box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 5);
    gtk_box_pack_start(GTK_BOX(vbox), header_box, FALSE, FALSE, 0);

    GtkWidget *title = gtk_label_new("StudyAI - MV");
    gtk_box_pack_start(GTK_BOX(header_box), title, TRUE, TRUE, 0);

    GtkWidget *theme_btn = gtk_button_new_with_label("🌙 Dark Mode");
    g_signal_connect(theme_btn, "clicked", G_CALLBACK(on_toggle_theme), NULL);
    gtk_box_pack_end(GTK_BOX(header_box), theme_btn, FALSE, FALSE, 0);

    // Chat Area
    text_view = gtk_text_view_new();
    gtk_text_view_set_editable(GTK_TEXT_VIEW(text_view), FALSE);
    gtk_text_view_set_cursor_visible(GTK_TEXT_VIEW(text_view), FALSE);
    gtk_text_view_set_wrap_mode(GTK_TEXT_VIEW(text_view), GTK_WRAP_WORD_CHAR);
    
    buffer = gtk_text_view_get_buffer(GTK_TEXT_VIEW(text_view));
    gtk_text_buffer_create_tag(buffer, "user", "weight", PANGO_WEIGHT_BOLD, "foreground", "#4e9a06", NULL); // Green for user
    gtk_text_buffer_create_tag(buffer, "bot", "foreground", "#729fcf", NULL); // Blue for bot
    gtk_text_buffer_create_tag(buffer, "system", "style", PANGO_STYLE_ITALIC, "foreground", "#888888", NULL);
    gtk_text_buffer_create_tag(buffer, "error", "weight", PANGO_WEIGHT_BOLD, "foreground", "#cc0000", NULL);

    GtkWidget *scrolled_window = gtk_scrolled_window_new(NULL, NULL);
    gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(scrolled_window), GTK_POLICY_AUTOMATIC, GTK_POLICY_AUTOMATIC);
    gtk_container_add(GTK_CONTAINER(scrolled_window), text_view);
    gtk_box_pack_start(GTK_BOX(vbox), scrolled_window, TRUE, TRUE, 0);

    // Input Area
    GtkWidget *input_box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 5);
    gtk_box_pack_start(GTK_BOX(vbox), input_box, FALSE, FALSE, 0);

    entry = gtk_entry_new();
    gtk_entry_set_placeholder_text(GTK_ENTRY(entry), "Type a message...");
    g_signal_connect(entry, "activate", G_CALLBACK(on_send_clicked), NULL);
    gtk_box_pack_start(GTK_BOX(input_box), entry, TRUE, TRUE, 0);

    send_btn = gtk_button_new_with_label("Send");
    g_signal_connect(send_btn, "clicked", G_CALLBACK(on_send_clicked), NULL);
    gtk_box_pack_start(GTK_BOX(input_box), send_btn, FALSE, FALSE, 0);

    gtk_widget_show_all(window);
    gtk_main();

    return 0;
}
